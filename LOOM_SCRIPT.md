Loom script (3 minutes)

Intro (15s):
- "Hi, I'm [Your Name]. This is a 3-minute demo of LinkPlease backend for the internship assignment. I start on [start_date]."

Demo (120s):
- Show the repo root and mention key files: `app/main.py`, `app/worker.py`, `app/services/dm_service.py`, `FAILURES.md`.
- In the running app (browser): Create a rule via `POST /rules` using the interactive console or ReDoc. Show response.
- Trigger a webhook with a matching comment via the console or `post_webhook_fix.py`. Show `/events` and `/jobs` updating.
- Show `/stats` updating (mention queued/sent numbers). Explain that acceptance vs delivery differs and we reconcile.

Tradeoff (30s):
- One tradeoff: I used an in-process worker and in-memory rate-limiter to keep the app simple; this risks losing in-flight retry state during restarts. With more time I'd use Redis/ durable queue to persist rate-limiter + job state and scale workers.

What I'd do with more time (20s):
- Replace in-memory rate-limiter with Redis, add containerized worker, add end-to-end integration tests that run a local simulated PseudoGram to reproduce edge-cases.

Closing (10s):
- Mention repo URL and deployed URL, and point to `FAILURES.md` for detailed caveats.
