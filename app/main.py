import os
import hmac
import hashlib
import base64

from dotenv import load_dotenv

# Load environment variables from .env (local development)
load_dotenv()

from typing import List
from collections import deque
from datetime import datetime

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Request,
    status,
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import engine, get_db
from .models import (
    Base,
    Rule,
    Event,
    DMJob,
    BlockedDuplicate,
    DeletedComment,
)
from .schemas import (
    RuleCreate,
    RuleResponse,
    WebhookEvent,
    EventResponse,
    JobResponse,
    StatsResponse,
)
from .worker import start_worker_thread
from .services.dm_service import PSEUDOGRAM_API_KEY


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="LinkPlease PseudoGram Automation API",
    version="1.0.0",
)


# ============================================================
# START BACKGROUND WORKER
# ============================================================

@app.on_event("startup")
def startup_event():
    start_worker_thread()


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "LinkPlease PseudoGram Automation",
    }


# ============================================================
# STATS
# Part A & B
# ============================================================

@app.get(
    "/stats",
    response_model=StatsResponse,
)
def get_stats(
    db: Session = Depends(get_db),
):
    """
    Returns live numbers for DMs processed.

    sent:
        DMs confirmed sent or delivered.

    failed:
        DMs permanently failed after retries.

    queued:
        DMs waiting or currently being processed.

    duplicates_blocked:
        Duplicate DM attempts for the same
        (user_id + rule_id) combination.
    """

    sent = (
        db.query(DMJob)
        .filter(
            DMJob.status.in_(["sent", "delivered"])
        )
        .count()
    )

    failed = (
        db.query(DMJob)
        .filter(
            DMJob.status == "failed"
        )
        .count()
    )

    queued = (
        db.query(DMJob)
        .filter(
            DMJob.status.in_(["queued", "processing"])
        )
        .count()
    )

    duplicates_blocked = (
        db.query(BlockedDuplicate)
        .count()
    )

    return {
        "sent": sent,
        "failed": failed,
        "queued": queued,
        "duplicates_blocked": duplicates_blocked,
    }


# ============================================================
# CREATE RULE
# POST /rules
# ============================================================

@app.post(
    "/rules",
    status_code=status.HTTP_201_CREATED,
    response_model=RuleResponse,
)
def create_rule(
    rule: RuleCreate,
    db: Session = Depends(get_db),
):
    """
    Creates a keyword automation rule.

    Example:
        keyword = "link"
        dm_message = "Here's your link!"
    """

    keyword = rule.keyword.strip()

    # Case-insensitive check for an existing rule
    existing_rule = (
        db.query(Rule)
        .filter(
            Rule.keyword.ilike(keyword)
        )
        .first()
    )

    if existing_rule:
        return {
            "rule_id": str(existing_rule.id),
            "keyword": existing_rule.keyword,
            "dm_message": existing_rule.dm_message,
        }

    new_rule = Rule(
        keyword=keyword,
        dm_message=rule.dm_message,
    )

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    return {
        "rule_id": str(new_rule.id),
        "keyword": new_rule.keyword,
        "dm_message": new_rule.dm_message,
    }


# ============================================================
# GET RULES
# GET /rules
# ============================================================

@app.get(
    "/rules",
    response_model=List[RuleResponse],
)
def get_rules(
    db: Session = Depends(get_db),
):
    rules = db.query(Rule).all()

    return [
        {
            "rule_id": str(rule.id),
            "keyword": rule.keyword,
            "dm_message": rule.dm_message,
        }
        for rule in rules
    ]


# ============================================================
# WEBHOOK
# POST /webhook
#
# IMPORTANT:
# We intentionally use Request instead of:
#
#     payload: WebhookEvent
#
# because Part B requires HMAC verification against the
# EXACT raw HTTP request body.
#
# openapi_extra is used only to make Swagger display the
# request body correctly.
# ============================================================

@app.post(
    "/webhook",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": [
                            "event_id",
                            "event_type",
                            "data"
                        ],
                        "properties": {
                            "event_id": {
                                "type": "string",
                                "example": "loom_demo_001"
                            },
                            "event_type": {
                                "type": "string",
                                "example": "comment.created"
                            },
                            "sent_at": {
                                "type": "string",
                                "nullable": True,
                                "example": "2026-08-17T22:00:00Z"
                            },
                            "data": {
                                "type": "object",
                                "required": [],
                                "properties": {
                                    "comment_id": {
                                        "type": "string",
                                        "nullable": True,
                                        "example": "loom_comment_001"
                                    },
                                    "post_id": {
                                        "type": "string",
                                        "nullable": True,
                                        "example": "loom_post_001"
                                    },
                                    "text": {
                                        "type": "string",
                                        "nullable": True,
                                        "example": "Can you send me the link?"
                                    },
                                    "created_at": {
                                        "type": "string",
                                        "nullable": True,
                                        "example": "2026-08-17T22:00:00Z"
                                    },
                                    "from": {
                                        "type": "object",
                                        "nullable": True,
                                        "properties": {
                                            "user_id": {
                                                "type": "string",
                                                "example": "loom_user_001"
                                            },
                                            "username": {
                                                "type": "string",
                                                "nullable": True,
                                                "example": "loom_user"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    # ========================================================
    # READ RAW REQUEST BODY
    # ========================================================

    raw_body = await request.body()

    # ========================================================
    # RECENT WEBHOOK DEBUG RECORDS
    # ========================================================

    if not hasattr(app.state, "recent_webhooks"):
        app.state.recent_webhooks = deque(maxlen=200)

    # ========================================================
    # PART B — HMAC SIGNATURE VERIFICATION
    # ========================================================

    signature_header = request.headers.get(
        "X-PseudoGram-Signature"
    )

    if signature_header:
        sig = signature_header.strip()

        if sig.startswith("sha256="):
            sig = sig[len("sha256="):]

        # ----------------------------------------------------
        # Candidate API keys
        # ----------------------------------------------------

        candidate_keys = []

        if PSEUDOGRAM_API_KEY:
            candidate_keys.append(
                PSEUDOGRAM_API_KEY
            )

        # Optional comma-separated aliases
        extra_keys = os.getenv(
            "PSEUDOGRAM_API_KEY_ALIASES",
            "",
        )

        if extra_keys:
            for key in extra_keys.split(","):
                key = key.strip()

                if key:
                    candidate_keys.append(key)

        # ----------------------------------------------------
        # Local .env fallback for local development
        # ----------------------------------------------------

        try:
            env_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                ".env",
            )

            env_path = os.path.abspath(env_path)

            if os.path.exists(env_path):
                with open(
                    env_path,
                    "r",
                    encoding="utf-8",
                ) as env_file:

                    for line in env_file:
                        if line.strip().startswith(
                            "PSEUDOGRAM_API_KEY="
                        ):
                            local_key = (
                                line.split("=", 1)[1]
                                .strip()
                            )

                            if local_key:
                                candidate_keys.append(
                                    local_key
                                )

                            break

        except Exception:
            pass

        # ----------------------------------------------------
        # Remove duplicate keys
        # ----------------------------------------------------

        candidate_keys = list(
            dict.fromkeys(candidate_keys)
        )

        # ----------------------------------------------------
        # Calculate HMAC-SHA256
        # ----------------------------------------------------

        computed_hexes = []
        computed_b64s = []

        matched = False

        for key in candidate_keys:

            try:
                digest = hmac.new(
                    key.encode("utf-8"),
                    raw_body,
                    hashlib.sha256,
                )

                computed_hex = digest.hexdigest()

                computed_b64 = base64.b64encode(
                    digest.digest()
                ).decode()

                computed_hexes.append(
                    computed_hex
                )

                computed_b64s.append(
                    computed_b64
                )

                if (
                    hmac.compare_digest(
                        sig,
                        computed_hex,
                    )
                    or
                    hmac.compare_digest(
                        sig,
                        computed_b64,
                    )
                ):
                    matched = True
                    break

            except Exception:
                continue

        # ----------------------------------------------------
        # Debug information
        # ----------------------------------------------------

        try:
            app.state.recent_webhooks.appendleft(
                {
                    "time": (
                        datetime.utcnow()
                        .isoformat()
                        + "Z"
                    ),
                    "header_sig": signature_header,
                    "computed_hexes": computed_hexes,
                    "computed_b64s": computed_b64s,
                    "matched": bool(matched),
                }
            )

        except Exception:
            pass

        # ----------------------------------------------------
        # Reject invalid signature
        # ----------------------------------------------------

        if not matched:
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature",
            )

    # ========================================================
    # PARSE AND VALIDATE JSON BODY
    # ========================================================

    try:
        body_json = await request.json()

        event = WebhookEvent.model_validate(
            body_json
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid webhook payload: "
                f"{str(exc)}"
            ),
        )

    # ========================================================
    # PART B — DUPLICATE EVENT PROTECTION
    # ========================================================

    existing_event = (
        db.query(Event)
        .filter(
            Event.event_id == event.event_id
        )
        .first()
    )

    if existing_event:
        return {
            "message": "duplicate event ignored"
        }

    # ========================================================
    # STORE EVENT
    # ========================================================

    new_event = Event(
        event_id=event.event_id,
        event_type=event.event_type,
    )

    db.add(new_event)

    try:
        db.commit()

    except IntegrityError:

        db.rollback()

        return {
            "message": "duplicate event ignored"
        }

    # ========================================================
    # PART C — comment.deleted
    # ========================================================

    if event.event_type == "comment.deleted":

        comment_id = event.data.comment_id

        if comment_id:

            # ------------------------------------------------
            # Store deleted comment
            # ------------------------------------------------

            existing_deleted = (
                db.query(DeletedComment)
                .filter(
                    DeletedComment.comment_id
                    == comment_id
                )
                .first()
            )

            if not existing_deleted:

                db.add(
                    DeletedComment(
                        comment_id=comment_id
                    )
                )

                try:
                    db.commit()

                except IntegrityError:

                    db.rollback()

            # ------------------------------------------------
            # Cancel queued/processing jobs
            # ------------------------------------------------

            pending_jobs = (
                db.query(DMJob)
                .filter(
                    DMJob.comment_id
                    == comment_id,
                    DMJob.status.in_(
                        [
                            "queued",
                            "processing",
                        ]
                    ),
                )
                .all()
            )

            for job in pending_jobs:
                job.status = "cancelled"

            db.commit()

        return {
            "message": (
                "comment.deleted event processed"
            )
        }

    # ========================================================
    # PROCESS COMMENT CREATED / ACCEPTED
    # ========================================================

    if event.event_type not in (
        "comment.created",
        "comment.accepted",
    ):

        return {
            "message": (
                "unhandled event type ignored"
            )
        }

    # ========================================================
    # VALIDATE COMMENT DATA
    # ========================================================

    if (
        not event.data.text
        or not event.data.from_
    ):

        return {
            "message": (
                "event missing required "
                "comment data"
            )
        }

    # ========================================================
    # COMMENT ID
    # ========================================================

    comment_id = event.data.comment_id

    # ========================================================
    # OUT-OF-ORDER DELETED COMMENT CHECK
    # ========================================================

    if comment_id:

        is_deleted = (
            db.query(DeletedComment)
            .filter(
                DeletedComment.comment_id
                == comment_id
            )
            .first()
        )

        if is_deleted:

            return {
                "message": (
                    "comment already deleted, "
                    "skipping DM"
                )
            }

    # ========================================================
    # COMMENT TEXT
    # ========================================================

    comment_text = event.data.text.lower()

    # ========================================================
    # USER ID
    # ========================================================

    user_id = event.data.from_.user_id

    # ========================================================
    # FIND MATCHING RULES
    # ========================================================

    rules = db.query(Rule).all()

    for rule in rules:

        # Case-insensitive keyword matching
        if rule.keyword.lower() in comment_text:

            # =================================================
            # PART A — USER + RULE DEDUPLICATION
            # =================================================

            existing_job = (
                db.query(DMJob)
                .filter(
                    DMJob.user_id == user_id,
                    DMJob.rule_id == rule.id,
                )
                .first()
            )

            if existing_job:

                # ---------------------------------------------
                # Record blocked duplicate
                # ---------------------------------------------

                blocked = BlockedDuplicate(
                    user_id=user_id,
                    rule_id=rule.id,
                    comment_id=comment_id,
                )

                db.add(blocked)
                db.commit()

                continue

            # =================================================
            # CREATE DM JOB
            # =================================================

            job = DMJob(
                user_id=user_id,
                rule_id=rule.id,
                comment_id=comment_id,
                message=rule.dm_message,
                status="queued",
                retry_count=0,
            )

            db.add(job)

            try:

                db.commit()

            except IntegrityError:

                # ---------------------------------------------
                # Concurrent duplicate protection
                # ---------------------------------------------

                db.rollback()

                blocked = BlockedDuplicate(
                    user_id=user_id,
                    rule_id=rule.id,
                    comment_id=comment_id,
                )

                db.add(blocked)
                db.commit()

    # ========================================================
    # RETURN IMMEDIATELY
    # ========================================================

    return {
        "message": "event processed"
    }


# ============================================================
# EVENTS
# GET /events
# ============================================================

@app.get(
    "/events",
    response_model=List[EventResponse],
)
def get_events(
    db: Session = Depends(get_db),
):
    return db.query(Event).all()


# ============================================================
# JOBS
# GET /jobs
# ============================================================

@app.get(
    "/jobs",
    response_model=List[JobResponse],
)
def get_jobs(
    db: Session = Depends(get_db),
):
    return db.query(DMJob).all()


# ============================================================
# SINGLE JOB
# GET /jobs/{job_id}
# ============================================================

@app.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):

    job = (
        db.query(DMJob)
        .filter(
            DMJob.id == job_id
        )
        .first()
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job


# ============================================================
# DEBUG — RECENT WEBHOOKS
# GET /debug/recent_webhooks
# ============================================================

@app.get(
    "/debug/recent_webhooks"
)
def recent_webhooks():
    """
    Returns recent webhook signature checks.

    WARNING:
    This endpoint is intended for debugging.
    Do not expose sensitive information in production.
    """

    entries = list(
        getattr(
            app.state,
            "recent_webhooks",
            [],
        )
    )

    return entries