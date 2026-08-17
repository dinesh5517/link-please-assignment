🚀 LinkPlease — PseudoGram Automation API

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white">
  <img src="https://img.shields.io/badge/Render-Live-46E3B7?style=for-the-badge&logo=render&logoColor=black">
</p>

<p align="center">
  <b>Keyword-based comment-to-DM automation backend built with FastAPI.</b>
</p>

🔗 1. Project Links

🔎 Resource

🔗 Link

🌐 Live API

Open Live API

📚 Swagger Documentation

Open /docs

📊 Live Statistics

Open /stats

📋 Rules

Open /rules

📨 Events

Open /events

⚙️ Jobs

Open /jobs

🐙 GitHub Repository

Open GitHub

📌 2. Project Overview

LinkPlease is a FastAPI backend that automates direct messages based on keywords found in user comments.

Basic workflow

User Comment
     ↓
POST /webhook
     ↓
HMAC Signature Verification
     ↓
Event Deduplication
     ↓
Keyword Rule Matching
     ↓
DM Job Created
     ↓
Background Worker
     ↓
PseudoGram API
     ↓
Delivery Reconciliation
     ↓
Delivered / Retry / Failed

🅰️ 3. Part A — Core Automation

3.1 Create a Rule

Endpoint

POST /rules

A rule contains:

keyword

dm_message

Example

{
  "keyword": "link",
  "dm_message": "Here's your link!"
}

If a comment contains:

Can you send me the link?

the backend identifies the keyword link and creates a DM job.

3.2 Webhook

Endpoint

POST /webhook

The webhook receives comment events from PseudoGram.

Supported comment events include:

comment.created
comment.accepted
comment.deleted

For a matching comment, a job is stored in the database with:

status = queued

The webhook returns quickly while the worker handles the actual DM.

3.3 Statistics

Endpoint

GET /stats

Example:

{
  "sent": 1,
  "failed": 0,
  "queued": 0,
  "duplicates_blocked": 0
}

Statistics meaning

Field

Meaning

sent

Sent or delivered DMs

failed

Permanently failed jobs

queued

Jobs waiting/processing

duplicates_blocked

Duplicate DM attempts prevented

🛡️ 4. Deduplication

The same user should not receive the same rule's DM repeatedly.

The database protects the combination:

(user_id, rule_id)

Example

User comments "link"
        ↓
DM sent

Same user comments "link" again
        ↓
Duplicate blocked

The duplicate attempt is recorded and counted in:

duplicates_blocked

🔐 5. Part B — Webhook Security

Every webhook can be verified using:

X-PseudoGram-Signature: sha256=<hex>

The server calculates:

HMAC-SHA256(
    raw_request_body,
    PSEUDOGRAM_API_KEY
)

and compares it with the received signature.

Security flow

Webhook Request
      ↓
Read raw body
      ↓
Verify HMAC-SHA256
      ↓
 ┌───────────────┐
 │               │
Valid           Invalid
 │               │
 ↓               ↓
Process         401

This prevents forged or modified webhook requests from being processed.

🔄 6. Duplicate Event Protection

Every event contains:

event_id

The event ID is stored in the database.

If the same event is received again:

{
  "message": "duplicate event ignored"
}

This protects the application from repeated webhook deliveries.

♻️ 7. Part C — Delivery Reconciliation

A 202 Accepted response from the external DM API does not necessarily mean that the DM was ultimately delivered.

The worker therefore checks the DM status after submission.

Flow

DM submitted
     ↓
202 Accepted
     ↓
Store dm_id
     ↓
Poll DM status
     ↓
 ┌───────────────┐
 │               │
DELIVERED       FAILED
 │               │
 ↓               ↓
Complete       Re-queue
                 ↓
               Retry
                 ↓
              Up to 3

This prevents silently losing failed messages.

🗑️ 8. Deleted Comment Handling

The backend handles:

comment.deleted

events.

Deleted before DM

Comment deleted
      ↓
Queued job cancelled

Deleted after DM

If the DM has already reached the external API, it cannot be recalled.

This limitation is documented in FAILURES.md.

🚦 9. Rate Limiting

The worker uses a sliding-window rate limiter.

Current limit

10 DMs per rolling 60 seconds

The system also handles API throttling and can back off when the external API returns rate-limit information.

🧵 10. Background Worker

The webhook does not perform the complete DM operation synchronously.

Instead:

Webhook
   ↓
Create DMJob
   ↓
Return response
   ↓
Background Worker
   ↓
Send DM
   ↓
Reconcile status

This keeps webhook processing fast and allows jobs to be retried.

🗂️ 11. Project Structure

link-please-assignment/
│
├── app/
│   ├── main.py              # FastAPI routes and webhook handling
│   ├── worker.py            # Background job processing
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic schemas
│   │
│   └── services/
│       └── dm_service.py    # PseudoGram API communication
│
├── requirements.txt
├── README.md
└── FAILURES.md

🧪 12. Live Testing

Step 1 — Create a Rule

Open:

👉 Swagger /docs

Select:

POST /rules

Use:

{
  "keyword": "link",
  "dm_message": "Here's your link!"
}

Step 2 — Send a Webhook

Select:

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

Note: If signature verification is enabled, the request must also contain a valid X-PseudoGram-Signature header.

Step 3 — Check the Result

Open:

👉 Live /stats

You can also inspect:

Rules

Events

Jobs

📡 13. API Reference

Method

Endpoint

Description

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

Receive webhook events

🟣 GET

/stats

View live statistics

🔵 GET

/events

View stored events

🟡 GET

/jobs

View DM jobs

🟡 GET

/jobs/{job_id}

View a specific job

⚪ GET

/debug/recent_webhooks

Debug webhook signatures

🏗️ 14. Architecture

                   ┌─────────────────────┐
                   │     PseudoGram      │
                   │   Comment Event     │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │    POST /webhook    │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ HMAC Verification   │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Event Deduplication │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  Keyword Matching   │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │     SQLite DB       │
                   │   DMJob = queued    │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Background Worker   │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  PseudoGram DM API  │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │   Reconciliation    │
                   └──────┬───────┬──────┘
                          │       │
                          ▼       ▼
                     Delivered   Failed
                                  │
                                  ▼
                                Retry

⚖️ 15. Engineering Tradeoff

Current approach

The rate limiter stores timestamps in memory.

Advantages

Simple implementation

No additional infrastructure

Fast

Easy to maintain

Limitation

A container restart clears the in-memory timestamps.

Production improvement

Use Redis for distributed and persistent rate limiting.

🚀 16. Future Improvements

With additional development time:

🔴 Replace the in-memory rate limiter with Redis.

🟣 Replace the daemon thread with a durable queue such as Celery.

🧪 Add integration tests with a local PseudoGram mock.

📦 Add dead-letter queue support.

📈 Add structured monitoring and metrics.

🔁 Add stronger exponential backoff.

🔒 Restrict debug endpoints in production.

🛠️ 17. Technology Stack

Technology

Purpose

🐍 Python

Backend language

⚡ FastAPI

REST API framework

🧩 Pydantic

Request/response validation

🗄️ SQLite

Persistent database

🧱 SQLAlchemy

ORM

🔐 HMAC-SHA256

Webhook security

🧵 Background Thread

Asynchronous job processing

☁️ Render

Deployment

🐙 GitHub

Source control

📹 18. Demo & Submission

🌐 Live Application

Open Live API

📚 API Documentation

Open Swagger

📊 Live Statistics

Open Stats

🐙 Source Code

Open GitHub Repository

👨‍💻 Author

Dinesh

LinkPlease Backend — Tech Intern Assignment

<p align="center">
  <b>⚡ FastAPI • 🔐 Secure Webhooks • 🧵 Background Jobs • ♻️ Retry • 📊 Reconciliation</b>
</p>
