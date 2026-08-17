import os
import hmac
import hashlib
from dotenv import load_dotenv

# Load environment variables from .env (local development)
load_dotenv()
from typing import List, Dict, Any
from collections import deque
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import engine, get_db
from .models import Base, Rule, Event, DMJob, BlockedDuplicate, DeletedComment
from .schemas import (
    RuleCreate,
    RuleResponse,
    WebhookEvent,
    EventResponse,
    JobResponse,
    StatsResponse
)
from .worker import start_worker_thread, _request_timestamps
from .services.dm_service import PSEUDOGRAM_API_KEY

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LinkPlease PseudoGram Automation API",
    version="1.0.0"
)

# Start background worker thread on app startup
@app.on_event("startup")
def startup_event():
    start_worker_thread()


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "LinkPlease PseudoGram Automation"
    }


# =========================
# STATS (Part A & B mandatory)
# =========================

@app.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """
    Returns live numbers for DMs processed:
    - sent: DMs confirmed sent or delivered
    - failed: DMs permanently failed after retries
    - queued: DMs waiting or currently being processed
    - duplicates_blocked: duplicate DM attempts for (user_id + rule_id) correctly blocked
    """
    sent = db.query(DMJob).filter(DMJob.status.in_(["sent", "delivered"])).count()
    failed = db.query(DMJob).filter(DMJob.status == "failed").count()
    queued = db.query(DMJob).filter(DMJob.status.in_(["queued", "processing"])).count()
    duplicates_blocked = db.query(BlockedDuplicate).count()

    return {
        "sent": sent,
        "failed": failed,
        "queued": queued,
        "duplicates_blocked": duplicates_blocked
    }


# =========================
# CREATE RULE
# =========================

@app.post(
    "/rules",
    status_code=status.HTTP_201_CREATED,
    response_model=RuleResponse
)
def create_rule(
    rule: RuleCreate,
    db: Session = Depends(get_db)
):
    keyword = rule.keyword.strip()

    # Case-insensitive check for existing rule
    existing_rule = db.query(Rule).filter(
        Rule.keyword.ilike(keyword)
    ).first()

    if existing_rule:
        return {
            "rule_id": str(existing_rule.id),
            "keyword": existing_rule.keyword,
            "dm_message": existing_rule.dm_message
        }

    new_rule = Rule(
        keyword=keyword,
        dm_message=rule.dm_message
    )

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    return {
        "rule_id": str(new_rule.id),
        "keyword": new_rule.keyword,
        "dm_message": new_rule.dm_message
    }


# =========================
# GET RULES
# =========================

@app.get("/rules", response_model=List[RuleResponse])
def get_rules(db: Session = Depends(get_db)):
    rules = db.query(Rule).all()
    return [
        {
            "rule_id": str(r.id),
            "keyword": r.keyword,
            "dm_message": r.dm_message
        }
        for r in rules
    ]


# =========================
# WEBHOOK
# =========================

@app.post("/webhook")
async def webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    raw_body = await request.body()

    # Record recent webhook handling attempts (in-memory, non-persistent)
    if not hasattr(app.state, "recent_webhooks"):
        app.state.recent_webhooks = deque(maxlen=200)

    # Part B: Webhook Signature Verification
    signature_header = request.headers.get("X-PseudoGram-Signature")
    if signature_header:
        sig = signature_header
        if sig.startswith("sha256="):
            sig = sig[len("sha256="):]

        # Compute both hex and base64 HMACs to accept either encoding from the sender
        computed_hex = hmac.new(
            PSEUDOGRAM_API_KEY.encode("utf-8"),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        computed_raw = hmac.new(
            PSEUDOGRAM_API_KEY.encode("utf-8"),
            raw_body,
            hashlib.sha256
        ).digest()
        try:
            import base64
            computed_b64 = base64.b64encode(computed_raw).decode()
        except Exception:
            computed_b64 = ""

        matched = (hmac.compare_digest(sig, computed_hex) or hmac.compare_digest(sig, computed_b64))

        # Save a short debug record (do not store secrets)
        try:
            app.state.recent_webhooks.appendleft({
                "time": datetime.utcnow().isoformat() + "Z",
                "header_sig": signature_header,
                "computed_hex": computed_hex,
                "computed_b64": computed_b64,
                "matched": bool(matched),
            })
        except Exception:
            pass

        if not matched:
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Parse body
    try:
        body_json = await request.json()
        event = WebhookEvent.model_validate(body_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {str(e)}")

    # 1. Deduplicate events (same event_id can repeat)
    existing_event = db.query(Event).filter(
        Event.event_id == event.event_id
    ).first()

    if existing_event:
        return {"message": "duplicate event ignored"}

    # Save event
    new_event = Event(
        event_id=event.event_id,
        event_type=event.event_type
    )
    db.add(new_event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"message": "duplicate event ignored"}

    # 2. Handle comment.deleted (Part C)
    if event.event_type == "comment.deleted":
        comment_id = event.data.comment_id
        if comment_id:
            # Record comment as deleted in case comment.deleted arrived before comment.created
            existing_del = db.query(DeletedComment).filter(
                DeletedComment.comment_id == comment_id
            ).first()
            if not existing_del:
                db.add(DeletedComment(comment_id=comment_id))
                try:
                    db.commit()
                except IntegrityError:
                    db.rollback()

            # Cancel any queued/processing jobs for this comment
            pending_jobs = db.query(DMJob).filter(
                DMJob.comment_id == comment_id,
                DMJob.status.in_(["queued", "processing"])
            ).all()
            for job in pending_jobs:
                job.status = "cancelled"
            db.commit()
        return {"message": "comment.deleted event processed"}

    # 3. Process comment.created or comment.accepted
    if event.event_type not in ("comment.created", "comment.accepted"):
        return {"message": "unhandled event type ignored"}

    if not event.data.text or not event.data.from_:
        return {"message": "event missing required comment data"}

    comment_id = event.data.comment_id

    # Check if comment was deleted prior to comment.created arriving (out-of-order delivery)
    if comment_id:
        is_deleted = db.query(DeletedComment).filter(
            DeletedComment.comment_id == comment_id
        ).first()
        if is_deleted:
            return {"message": "comment already deleted, skipping DM"}

    comment_text = event.data.text.lower()
    user_id = event.data.from_.user_id

    # Find matching rules
    rules = db.query(Rule).all()

    for rule in rules:
        if rule.keyword.lower() in comment_text:
            # Check duplicate rule for same user (The same user NEVER gets DMed twice for the same rule)
            existing_job = db.query(DMJob).filter(
                DMJob.user_id == user_id,
                DMJob.rule_id == rule.id
            ).first()

            if existing_job:
                # Record blocked duplicate
                blocked = BlockedDuplicate(
                    user_id=user_id,
                    rule_id=rule.id,
                    comment_id=comment_id
                )
                db.add(blocked)
                db.commit()
                continue

            # Create new DMJob
            job = DMJob(
                user_id=user_id,
                rule_id=rule.id,
                comment_id=comment_id,
                message=rule.dm_message,
                status="queued",
                retry_count=0
            )
            db.add(job)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                # Unique constraint (user_id, rule_id) triggered concurrently
                blocked = BlockedDuplicate(
                    user_id=user_id,
                    rule_id=rule.id,
                    comment_id=comment_id
                )
                db.add(blocked)
                db.commit()

    return {"message": "event processed"}


# =========================
# DEBUG / INSPECTION ENDPOINTS
# =========================

@app.get("/events", response_model=List[EventResponse])
def get_events(db: Session = Depends(get_db)):
    return db.query(Event).all()


@app.get("/jobs", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(DMJob).all()


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(DMJob).filter(DMJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get('/debug/recent_webhooks')
def recent_webhooks():
    """Return recent webhook signature checks for debugging (no secrets returned)."""
    entries = list(getattr(app.state, "recent_webhooks", []))
    return entries