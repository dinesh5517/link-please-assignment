# Link-Please
🚀 LinkPlease — PseudoGram Automation API

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render&logoColor=black" alt="Render">
</p>

<p align="center">
  <b>Keyword-based comment-to-DM automation backend built with FastAPI.</b>
</p>

🔗 Live Project Links

Resource

Link

🌐 Live API

🔵 Open Live API

📚 Swagger API Docs

🟢 Open Swagger /docs

📊 Live Statistics

🟠 Open /stats

🐙 GitHub Repository

⚫ Open GitHub Repository

📋 API Rules

🟣 Open /rules

📨 Events

🔵 Open /events

⚙️ Jobs

🟡 Open /jobs

🎯 Project Overview

LinkPlease is a FastAPI backend that automatically sends a direct message when a user's comment contains a configured keyword.

Example

A rule can be created as:

{
  "keyword": "link",
  "dm_message": "Here's your link!"
}

When a user comments:

Can you send me the link?

the system:

Comment
   ↓
Webhook
   ↓
HMAC-SHA256 verification
   ↓
Event deduplication
   ↓
Keyword matching
   ↓
DM job queued
   ↓
Background worker
   ↓
PseudoGram API
   ↓
Delivery reconciliation
   ↓
Delivered / Retry / Failed

✨ Features

🅰️ Part A — Core Automation

POST /rules

Creates a keyword automation rule.

Example:

{
  "keyword": "link",
  "dm_message": "Here's your link!"
}

POST /webhook

Receives comment events and checks them against all configured rules.

Matching is:

✅ Case-insensitive

✅ Database-backed

✅ Processed asynchronously

✅ Protected against duplicate DMs

GET /stats

Returns:

{
  "sent": 1,
  "failed": 0,
  "queued": 0,
  "duplicates_blocked": 0
}

🔐 Part B — Webhook Security

Every signed webhook can use:

X-PseudoGram-Signature: sha256=<hex>

The backend calculates:

HMAC-SHA256(raw_request_body, API_KEY)

and compares the result using a secure comparison.

Security behavior

Valid signature
      ↓
   Process

Invalid signature
      ↓
401 Unauthorized

The raw request body is verified before JSON processing so that the signature represents the exact received payload.

♻️ Part C — Delivery Reconciliation

A successful API acceptance does not necessarily mean the DM was delivered.

The worker tracks the returned DM ID and checks its status.

202 Accepted
     ↓
Poll DM status
     ↓
 ┌───────────────┐
 │               │
Delivered      Failed
 │               │
 ↓               ↓
Complete       Retry
                 │
                 ↓
             Up to 3

This prevents silently losing messages after an API-side failure.

🛡️ Deduplication

The database protects against duplicate DMs using the combination:

(user_id, rule_id)

Therefore, if the same user comments multiple times with the same keyword, the same rule will not send the DM repeatedly.

Duplicate attempts are recorded in:

BlockedDuplicate

and exposed through:

GET /stats

📨 Duplicate Event Protection

Each incoming webhook contains an:

event_id

The event ID is stored in the database.

If the same event is received again:

{
  "message": "duplicate event ignored"
}

This protects the system from repeated webhook deliveries.

🗑️ Deleted Comment Handling

The backend handles:

comment.deleted

events.

If the comment is deleted before the DM is sent

The queued job is cancelled.

If the DM has already been sent

The message cannot be recalled from the external API, so this behavior is documented as a known limitation.

🚦 Rate Limiting

The background worker uses a sliding-window rate limiter.

Configured limit:

10 DMs / 60 seconds

The worker also handles API throttling using the API's retry information when available.

🧵 Background Processing

The webhook endpoint returns quickly while the actual DM work is performed by the background worker.

Main components:

app/main.py
    ↓
Webhook + API routes

app/worker.py
    ↓
Background job processing

app/services/dm_service.py
    ↓
PseudoGram API communication

app/models.py
    ↓
Database models

app/schemas.py
    ↓
Pydantic request/response validation

app/database.py
    ↓
Database connection

🗂️ Project Structure

link-please-assignment/
│
├── app/
│   ├── main.py
│   ├── worker.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   └── services/
│       └── dm_service.py
│
├── requirements.txt
├── README.md
└── FAILURES.md

🧪 Testing the API

1. Create a Rule

Open:

🟢 Swagger API Docs

Use:

POST /rules

Request:

{
  "keyword": "link",
  "dm_message": "Here's your link!"
}

2. Send a Webhook

Use:

POST /webhook

Example payload:

{
  "event_id": "loom_demo_001",
  "event_type": "comment.created",
  "sent_at": "2026-08-17T22:00:00Z",
  "data": {
    "comment_id": "loom_comment_001",
    "post_id": "loom_post_001",
    "text": "Can you send me the link?",
    "created_at": "2026-08-17T22:00:00Z",
    "from": {
      "user_id": "loom_user_001",
      "username": "loom_user"
    }
  }
}

3. Check Statistics

Open:

🟠 Live /stats

Example:

{
  "sent": 1,
  "failed": 0,
  "queued": 0,
  "duplicates_blocked": 0
}

📡 API Endpoints

Method

Endpoint

Purpose

🟢 GET

/

API health/status

🟠 POST

/rules

Create keyword rule

🔵 GET

/rules

List rules

🔴 POST

/webhook

Receive comment webhook

🟣 GET

/stats

Live DM statistics

🔵 GET

/events

View stored events

🟡 GET

/jobs

View DM jobs

🟡 GET

/jobs/{job_id}

View one DM job

⚪ GET

/debug/recent_webhooks

Debug webhook signatures

🏗️ Technology Stack

🐍 Python

⚡ FastAPI

🧩 Pydantic

🗄️ SQLite

🧱 SQLAlchemy

🔐 HMAC-SHA256

🧵 Background worker thread

☁️ Render

🐙 GitHub

📊 Architecture

                 ┌─────────────────────┐
                 │   PseudoGram Event  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ POST /webhook       │
                 └──────────┬──────────┘
                            │
                    HMAC Verification
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Event Deduplication │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Keyword Rule Match  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ SQLite DM Job       │
                 │ status = queued     │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Background Worker   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ PseudoGram DM API   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Reconciliation      │
                 └──────┬───────┬──────┘
                        │       │
                   Delivered   Failed
                        │       │
                        ▼       ▼
                     Done     Retry

⚖️ Engineering Tradeoff

The current rate limiter keeps request timestamps in memory.

Advantage

Simple

No additional infrastructure

Fast

Easy to maintain

Limitation

If the container restarts, the in-memory sliding window is reset.

A production-scale implementation could use:

Redis

for distributed and persistent rate limiting.

🚀 Future Improvements

With additional development time:

🔴 Replace the in-memory rate limiter with Redis.

🟣 Replace the daemon worker thread with Celery or another durable job queue.

🧪 Add integration tests using a local PseudoGram API mock.

📦 Add dead-letter queue support.

📈 Add structured monitoring and metrics.

🔁 Add more robust exponential backoff.

🔒 Restrict debug endpoints in production.

📹 Demo

The live deployment can be demonstrated through:

🌐 Live API

🔵 https://link-please-assignment.onrender.com/

📚 Swagger

🟢 https://link-please-assignment.onrender.com/docs

📊 Statistics

🟠 https://link-please-assignment.onrender.com/stats

🐙 Source Code

⚫ https://github.com/dinesh5517/link-please-assignment

👨‍💻 Author

Dinesh

Built for the Tech Intern / LinkPlease Backend Assignment.

<p align="center">
  <b>🚀 FastAPI • Webhooks • HMAC • Background Jobs • Retry • Reconciliation</b>
</p>
