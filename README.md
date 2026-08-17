<div align="center">

# 🚀 LinkPlease
### PseudoGram Automation API

Keyword-based comment-to-DM automation backend built with **FastAPI**.

<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white">
<img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black">

</div>

---

## 🔗 Live Links

| | |
|---|---|
| 🌐 **Live API** | [link-please-assignment.onrender.com](https://link-please-assignment.onrender.com/) |
| 📚 **Swagger Docs** | [/docs](https://link-please-assignment.onrender.com/docs) |
| 📊 **Live Stats** | [/stats](https://link-please-assignment.onrender.com/stats) |
| 📋 **Rules** | [/rules](https://link-please-assignment.onrender.com/rules) |
| 📨 **Events** | [/events](https://link-please-assignment.onrender.com/events) |
| ⚙️ **Jobs** | [/jobs](https://link-please-assignment.onrender.com/jobs) |
| 🐙 **GitHub** | [dinesh5517/link-please-assignment](https://github.com/dinesh5517/link-please-assignment) |

---

## 📌 What This Project Does

LinkPlease automatically sends a DM when a comment contains a configured keyword.

```
Comment → Webhook → Verify Signature → Match Keyword
   → Create DM Job → Background Worker → Send DM
   → Check Delivery → Delivered / Retry / Failed
```

---

## 🅰️ Part A — Core Automation

### 1. Create a Rule
`POST /rules`
```json
{
  "keyword": "link",
  "dm_message": "Here's your link!"
}
```

### 2. Receive a Webhook
`POST /webhook`

The server:
- ✅ Checks the incoming event
- ✅ Matches the comment against rules
- ✅ Creates a DM job
- ✅ Prevents duplicate DMs
- ✅ Processes the job in the background

### 3. View Statistics
`GET /stats`
```json
{
  "sent": 1,
  "failed": 0,
  "queued": 0,
  "duplicates_blocked": 0
}
```

---

## 🛡️ Deduplication

The same user **cannot** receive the same rule's DM twice.
Protected at the DB level by **`(user_id + rule_id)`**.

```
User comments "link"        → DM sent
Same user comments "link"   → Duplicate blocked ✋
```

---

## 🔐 Part B — Webhook Security

Every webhook carries:
```
X-PseudoGram-Signature: sha256=<hex>
```

Verified as:
```
HMAC-SHA256(raw_body, API_KEY)
```

| Result | Response |
|---|---|
| ✅ Correct signature | Process webhook |
| ❌ Wrong signature | `401 Unauthorized` |

### 🔄 Duplicate Event Protection
Every webhook has an `event_id`, stored in the DB. A repeat returns:
```json
{ "message": "duplicate event ignored" }
```

---

## ♻️ Part C — Delivery Reconciliation

A `202 Accepted` doesn't always mean the DM was delivered — the worker checks status and retries.

```
DM Accepted → Check Status
                ├── Delivered → Done ✅
                └── Failed    → Retry (up to 3) 🔁
```

### 🗑️ Deleted Comments
- `comment.deleted` cancels a still-**queued** job.
- If the DM already reached the external API, it **can't** be recalled.

### 🚦 Rate Limiting
Sliding-window limiter: **10 DMs / 60 seconds**, plus backoff on upstream rate-limit responses.

---

## 🧵 Background Worker

The webhook responds fast; the actual send happens off the request path.

```
POST /webhook → Save DMJob → Return response
              → Background Worker → Send + Reconcile
```

---

## 🗂️ Project Structure

```
link-please-assignment/
│
├── app/
│   ├── main.py              # API routes & webhook handling
│   ├── worker.py             # Background DM processing
│   ├── database.py           # Database configuration
│   ├── models.py              # Database models
│   ├── schemas.py             # Request/response validation
│   └── services/
│       └── dm_service.py      # PseudoGram API calls
│
├── requirements.txt
├── README.md
└── FAILURES.md                # Known failures and tradeoffs
```

---

## 📡 API Endpoints

| Method | Endpoint | Purpose |
|:---:|---|---|
| 🟢 `GET` | `/` | Health check |
| 🟠 `POST` | `/rules` | Create rule |
| 🔵 `GET` | `/rules` | List rules |
| 🔴 `POST` | `/webhook` | Receive webhook |
| 🟣 `GET` | `/stats` | View statistics |
| 🔵 `GET` | `/events` | View events |
| 🟡 `GET` | `/jobs` | View DM jobs |
| 🟡 `GET` | `/jobs/{job_id}` | View one job |

---

## 🧪 Quick Live Test

**Step 1 — Create Rule**
Open [`/docs`](https://link-please-assignment.onrender.com/docs) → `POST /rules`
```json
{
  "keyword": "link",
  "dm_message": "Here's your link!"
}
```

**Step 2 — Send Webhook**
`POST /webhook`
```json
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
```

**Step 3 — Check Stats**
Open [`/stats`](https://link-please-assignment.onrender.com/stats) →
```json
{ "sent": 1, "failed": 0, "queued": 0, "duplicates_blocked": 0 }
```

---

## 🏗️ Architecture

```
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
```

---

## ⚖️ Main Tradeoff

> **Current:** the rate limiter stores timestamps in memory — simple, fast, no extra service required, but a restart clears them.
>
> **Future:** move to **Redis** for persistent, distributed rate limiting.

---

## 🚀 Future Improvements

- 🔴 Redis-based rate limiter
- 🟣 Celery or durable job queue
- 🧪 More integration tests
- 📦 Dead-letter queue
- 📈 Better monitoring
- 🔁 Exponential backoff
- 🔒 Secure production debug endpoints

---

## 🛠️ Tech Stack

**Backend** — 🐍 Python · ⚡ FastAPI · 🧩 Pydantic
**Database** — 🗄️ SQLite · 🧱 SQLAlchemy
**Security** — 🔐 HMAC-SHA256
**Deployment** — ☁️ Render · 🐙 GitHub

---

## 📹 Demo

🌐 [Live](https://link-please-assignment.onrender.com/) · 📚 [Swagger](https://link-please-assignment.onrender.com/docs) · 📊 [Stats](https://link-please-assignment.onrender.com/stats) · 🐙 [GitHub](https://github.com/dinesh5517/link-please-assignment)

---

<div align="center">

### 👨‍💻 Author

**Dinesh**
LinkPlease — Tech Intern Assignment

**⚡ FastAPI • 🔐 Webhooks • 🧵 Background Jobs • ♻️ Retry • 📊 Reconciliation**

</div>
