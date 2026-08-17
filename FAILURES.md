# System Known Failure Modes & Tradeoffs

Below is an honest, specific breakdown of scenarios in which this system can delay a DM, report transient stats, or encounter rate limit edge cases.

---

### 1. In-Memory Rate Limiter Window Loss on Process Restart
* **Condition:** The backend process or background worker restarts (e.g., container restart, deployment) during or immediately following a burst of DM dispatches.
* **Impact:** The sliding-window rate limiter (`_request_timestamps`) resides in process memory. On restart, the sliding window is cleared. If 10 requests were sent right before restart, the newly started worker has no memory of those requests and may attempt to dispatch new DMs immediately, triggering a `429 Rate Limited` response from PseudoGram.
* **Mitigation / Reality:** The system catches the 429 response, reads the `Retry-After` header, and pauses processing, leaving queued jobs safe for retry; however, a temporary rate-limit hit occurs on the API provider side.

---

### 2. Microsecond Concurrent Webhook Race Conditions
* **Condition:** Two identical webhook events or two comments from the same user matching the same rule arrive concurrently within <10ms across multiple threads or app workers.
* **Impact:** Both requests execute the `db.query(DMJob).filter(...)` check concurrently before either transaction is committed, passing the duplicate check in memory.
* **Mitigation / Reality:** The database level `UniqueConstraint(user_id, rule_id)` catches the duplicate on `db.commit()` and raises an `IntegrityError`. The endpoint catches this exception, rolls back, and logs it to `BlockedDuplicate`. Under SQLite single-writer lock contention, brief retry delays can occur.

---

### 3. Asynchronous Delivery Status Reconciliation Delays
* **Condition:** PseudoGram returns `202 Accepted` (`status: "queued"`) for a DM, but later marks the DM as `failed` on its internal server side.
* **Impact:** The system marks the job status as `sent` upon API acceptance. Status reconciliation depends on the background worker thread calling `GET /v1/dm/{dm_id}`. Under heavy rate-limiting or heavy job queues, status reconciliation may lag by several seconds or minutes, temporarily counting a DM in `/stats` as `sent` before discovering it failed on PseudoGram's side and re-queuing it.

---

### 4. Comment Deleted After API Acceptance
* **Condition:** A `comment.deleted` event arrives *after* `POST /v1/dm/send` has already returned `202 Accepted` from PseudoGram.
* **Impact:** If `comment.deleted` arrives while the job is still `queued` or `processing`, our system cancels the job. However, if PseudoGram has already accepted the DM for dispatch, the external API does not support canceling in-flight DMs, so the recipient will still receive the DM despite the comment deletion.
