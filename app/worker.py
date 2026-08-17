import time
from datetime import datetime, timedelta
import threading
import logging
from typing import List

from .database import SessionLocal
from .models import DMJob
from .services.dm_service import (
    send_dm,
    get_dm_status,
    RateLimitError,
    TemporaryAPIError,
    FatalAPIError
)

logger = logging.getLogger("dm_worker")
logging.basicConfig(level=logging.INFO)

MAX_RETRIES = 3
SLEEP_TIME = 1.0

# Rate limiter state: 10 requests per rolling 60 seconds
_request_timestamps: List[float] = []
_rate_limit_lock = threading.Lock()


def _enforce_rate_limit():
    """
    Ensures no more than 10 requests are sent in any rolling 60-second window.
    """
    global _request_timestamps
    with _rate_limit_lock:
        now = time.time()
        # Filter timestamps within the last 60 seconds
        _request_timestamps = [t for t in _request_timestamps if now - t < 60.0]

        if len(_request_timestamps) >= 10:
            # Sleep until the oldest request in the window expires
            sleep_needed = 60.0 - (now - _request_timestamps[0]) + 0.5
            if sleep_needed > 0:
                logger.info(f"Rate limiter active: sleeping {sleep_needed:.2f} seconds...")
                time.sleep(sleep_needed)
            # Re-filter after sleep
            now = time.time()
            _request_timestamps = [t for t in _request_timestamps if now - t < 60.0]

        _request_timestamps.append(time.time())


def process_jobs():
    """
    Processes 'queued' jobs and reconciles 'sent' jobs.
    """
    db = SessionLocal()
    try:
        # 1. Fetch queued jobs
        jobs = db.query(DMJob).filter(
            DMJob.status == "queued"
        ).order_by(DMJob.created_at.asc()).all()

        for job in jobs:
            # Re-check status in case it was cancelled by comment.deleted
            db.refresh(job)
            if job.status != "queued":
                continue

            job.status = "processing"
            job.last_attempt = datetime.utcnow()
            db.commit()

            try:
                _enforce_rate_limit()

                # Idempotency key per job attempt
                idempotency_key = f"job_{job.id}_try_{job.retry_count}"

                response = send_dm(
                    recipient_user_id=job.user_id,
                    message=job.message,
                    comment_id=job.comment_id,
                    idempotency_key=idempotency_key
                )

                dm_id = response.get("dm_id")
                job.dm_id = dm_id
                job.status = "sent"
                job.error_message = None
                logger.info(f"Job {job.id} DM sent. dm_id: {dm_id}")

            except RateLimitError as rle:
                logger.warning(f"Rate limited on job {job.id}: {rle.message}. Sleeping {rle.retry_after}s.")
                job.status = "queued"
                db.commit()
                time.sleep(rle.retry_after)
                break  # Stop processing further jobs in this batch until rate limit resets

            except TemporaryAPIError as tae:
                job.retry_count += 1
                job.error_message = str(tae)
                if job.retry_count >= MAX_RETRIES:
                    job.status = "failed"
                    logger.error(f"Job {job.id} failed after {MAX_RETRIES} retries: {tae}")
                else:
                    job.status = "queued"
                    logger.warning(f"Job {job.id} retry {job.retry_count}/{MAX_RETRIES}: {tae}")

            except FatalAPIError as fae:
                job.status = "failed"
                job.error_message = str(fae)
                logger.error(f"Job {job.id} fatal error: {fae}")

            except Exception as e:
                job.retry_count += 1
                job.error_message = f"Unexpected error: {str(e)}"
                if job.retry_count >= MAX_RETRIES:
                    job.status = "failed"
                else:
                    job.status = "queued"
                logger.error(f"Job {job.id} unhandled exception: {e}")

            db.commit()

        # 2. Reconcile 'sent' jobs to verify actual delivery (Part C)
        sent_jobs = db.query(DMJob).filter(
            DMJob.status == "sent",
            DMJob.dm_id.isnot(None)
        ).all()

        for job in sent_jobs:
            try:
                res = get_dm_status(job.dm_id)
                status = res.get("status")
                if status == "delivered":
                    job.status = "delivered"
                    logger.info(f"Job {job.id} reconciled: DELIVERED")
                    db.commit()
                elif status == "failed":
                    logger.warning(f"Job {job.id} reconciled: DM FAILED on API side!")
                    if job.retry_count < MAX_RETRIES:
                        job.retry_count += 1
                        job.status = "queued"
                        job.dm_id = None
                        logger.info(f"Job {job.id} re-queued for retry ({job.retry_count}/{MAX_RETRIES})")
                    else:
                        job.status = "failed"
                    db.commit()
            except Exception as e:
                logger.debug(f"Error checking status for dm_id {job.dm_id}: {e}")

    finally:
        db.close()


def run_worker_loop():
    logger.info("DM Worker Started")
    while True:
        try:
            process_jobs()
        except Exception as e:
            logger.error(f"Error in worker main loop: {e}")
        time.sleep(SLEEP_TIME)


def start_worker_thread():
    t = threading.Thread(target=run_worker_loop, daemon=True)
    t.start()
    return t


if __name__ == "__main__":
    run_worker_loop()
