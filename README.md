🚀 LinkPlease — PseudoGram Automation API

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white">
  <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black">
</p>

Keyword-based comment-to-DM automation backend built with FastAPI.

🔗 Live Links

🌐 Live API: https://link-please-assignment.onrender.com/

📚 Swagger Docs: https://link-please-assignment.onrender.com/docs

📊 Live Stats: https://link-please-assignment.onrender.com/stats

📋 Rules: https://link-please-assignment.onrender.com/rules

📨 Events: https://link-please-assignment.onrender.com/events

⚙️ Jobs: https://link-please-assignment.onrender.com/jobs

🐙 GitHub: https://github.com/dinesh5517/link-please-assignment

📌 What This Project Does

LinkPlease automatically sends a DM when a comment contains a configured keyword.

Comment
   ↓
Webhook
   ↓
Verify Signature
   ↓
Match Keyword
   ↓
Create DM Job
   ↓
Background Worker
   ↓
Send DM
   ↓
Check Delivery
   ↓
Delivered / Retry / Failed

🅰️ Part A — Core Automation

1. Create a Rule

POST /rules

Example:

{
  "keyword": "link",
  "dm_message": "Here's your link!"
}

2. Receive a Webhook

POST /webhook

The server:

Checks the incoming event

Matches the comment against rules

Creates a DM job

Prevents duplicate DMs

Processes the job in the background

3. View Statistics

GET /stats

Example:

{
  "sent": 1,
  "failed": 0,
  "queued": 0,
  "duplicates_blocked": 0
}

🛡️ Deduplication

The same user cannot receive the same rule's DM twice.

The database protects:

(user_id + rule_id)

Example:

User comments "link"
        ↓
DM sent

Same user comments "link" again
        ↓
Duplicate blocked

🔐 Part B — Webhook Security

Webhooks can contain:

X-PseudoGram-Signature: sha256=<hex>

The server verifies:

HMAC-SHA256(raw_body, API_KEY)

Result

Correct signature  →  Process webhook
Wrong signature    →  401 Unauthorized

This prevents forged or modified webhook requests.

🔄 Duplicate Event Protection

Every webhook contains an event_id.

The event ID is stored in the database.

If the same event is received again:

{
  "message": "duplicate event ignored"
}

♻️ Part C — Delivery Reconciliation

A 202 Accepted response does not always mean the DM was delivered.

The worker checks the DM status.

DM Accepted
    ↓
Check Status
    ↓
 ┌───────────┐
 │           │
Delivered   Failed
 │           │
 ↓           ↓
Done       Retry
             ↓
          Up to 3

This prevents silent message loss.

🗑️ Deleted Comments

The backend handles:

comment.deleted

If a comment is deleted before the DM is sent, the queued job is cancelled.

If the DM has already reached the external API, it cannot be recalled.

🚦 Rate Limiting

The worker uses a sliding-window rate limiter:

10 DMs / 60 seconds

The worker also handles API rate-limit responses and backs off when required.

🧵 Background Worker

The webhook returns quickly.

The actual DM processing happens in the worker:

POST /webhook
      ↓
Save DMJob
      ↓
Return response
      ↓
Background Worker
      ↓
Send + Reconcile

🗂️ Project Structure

link-please-assignment/
│
├── app/
│   ├── main.py
│   ├── worker.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── services/
│       └── dm_service.py
│
├── requirements.txt
├── README.md
└── FAILURES.md

Important Files

File

Purpose

main.py

API routes and webhook handling

worker.py

Background DM processing

models.py

Database models

schemas.py

Request/response validation

database.py

Database configuration

dm_service.py

PseudoGram API calls

FAILURES.md

Known failures and tradeoffs

📡 API Endpoints

Method

Endpoint

Purpose

🟢 GET

/

Health check

🟠 POST

/rules

Create rule

🔵 GET

/rules

List rules

🔴 POST

/webhook

Receive webhook

🟣 GET

/stats

View statistics

🔵 GET

/events

View events

🟡 GET

/jobs

View DM jobs

🟡 GET

/jobs/{job_id}

View one job

🧪 Quick Live Test

Step 1 — Create Rule

Open:

👉 https://link-please-assignment.onrender.com/docs

Choose:

POST /rules

Send:

{
  "keyword": "link",
  "dm_message": "Here's your link!"
}

Step 2 — Send Webhook

Choose:

POST /webhook

Send:

{
  "event_id": "demo_001",
  "event_type": "comment.created",
  "sent_at": "2026-08-17T22:00:00Z",
  "data": {
    "comment_id": "comment_001",
    "post_id": "post_001",
    "text": "Can you send me the link?",
    "created_at": "2026-08-17T22:00:00Z",
    "from": {
      "user_id": "user_001",
      "username": "demo_user"
    }
  }
}

Step 3 — Check Stats

Open:

👉 https://link-please-assignment.onrender.com/stats

Expected example:

sent: 1
failed: 0
queued: 0
duplicates_blocked: 0

🏗️ Architecture

             PseudoGram
                 │
                 ▼
          POST /webhook
                 │
                 ▼
        HMAC Verification
                 │
                 ▼
        Event Deduplication
                 │
                 ▼
         Keyword Matching
                 │
                 ▼
             SQLite
                 │
                 ▼
        Background Worker
                 │
                 ▼
          PseudoGram API
                 │
                 ▼
         Reconciliation
            /        \
           ▼          ▼
      Delivered      Failed
                       │
                       ▼
                     Retry

⚖️ Main Tradeoff

Current

The rate limiter stores timestamps in memory.

Advantages

Simple

Fast

No extra service required

Limitation

A restart clears the timestamps.

Future

Use Redis for persistent/distributed rate limiting.

🚀 Future Improvements

🔴 Redis-based rate limiter

🟣 Celery or durable job queue

🧪 More integration tests

📦 Dead-letter queue

📈 Better monitoring

🔁 Exponential backoff

🔒 Secure production debug endpoints

🛠️ Tech Stack

Backend

🐍 Python

⚡ FastAPI

🧩 Pydantic

Database

🗄️ SQLite

🧱 SQLAlchemy

Security

🔐 HMAC-SHA256

Deployment

☁️ Render

🐙 GitHub

📹 Demo

🌐 Live:
https://link-please-assignment.onrender.com/

📚 Swagger:
https://link-please-assignment.onrender.com/docs

📊 Stats:
https://link-please-assignment.onrender.com/stats

🐙 GitHub:
https://github.com/dinesh5517/link-please-assignment

👨‍💻 Author

Dinesh

LinkPlease — Tech Intern Assignment

<p align="center">
  <b>⚡ FastAPI • 🔐 Webhooks • 🧵 Background Jobs • ♻️ Retry • 📊 Reconciliation</b>
</p>
