<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

:root{
  --bg:#0B1120;
  --surface:#111A2E;
  --surface2:#16213A;
  --line:#243052;
  --text:#E7ECF7;
  --muted:#8B98B8;
  --green:#34D399;
  --orange:#FB923C;
  --blue:#60A5FA;
  --red:#F87171;
  --purple:#C084FC;
  --yellow:#FBBF24;
}

*{box-sizing:border-box;}
.lp-wrap{
  background:var(--bg);
  color:var(--text);
  font-family:'Inter',sans-serif;
  padding:48px 20px 64px;
  border-radius:16px;
}
.lp-inner{max-width:880px;margin:0 auto;}

.lp-eyebrow{
  font-family:'IBM Plex Mono',monospace;
  font-size:12px;
  letter-spacing:.14em;
  text-transform:uppercase;
  color:var(--green);
  margin:0 0 10px;
}
.lp-h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:38px;
  font-weight:700;
  margin:0 0 8px;
  line-height:1.15;
}
.lp-h1 span{color:var(--orange);}
.lp-sub{
  color:var(--muted);
  font-size:15.5px;
  margin:0 0 32px;
  max-width:560px;
}

/* pipeline hero */
.lp-pipeline{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  align-items:center;
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:12px;
  padding:20px;
  margin-bottom:40px;
}
.lp-node{
  font-family:'IBM Plex Mono',monospace;
  font-size:12.5px;
  padding:8px 12px;
  border-radius:7px;
  background:var(--surface2);
  border:1px solid var(--line);
  white-space:nowrap;
  opacity:0;
  animation:lp-pop .5s ease forwards;
}
.lp-node.g{color:var(--green);border-color:#1f5a45;}
.lp-node.o{color:var(--orange);border-color:#6b4222;}
.lp-node.b{color:var(--blue);border-color:#28466f;}
.lp-node.p{color:var(--purple);border-color:#4b3068;}
.lp-node.r{color:var(--red);border-color:#6a2c2c;}
.lp-arrow{color:var(--muted);font-size:13px;}
@keyframes lp-pop{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:translateY(0);}}
.lp-node:nth-child(1){animation-delay:.05s}
.lp-node:nth-child(3){animation-delay:.15s}
.lp-node:nth-child(5){animation-delay:.25s}
.lp-node:nth-child(7){animation-delay:.35s}
.lp-node:nth-child(9){animation-delay:.45s}
.lp-node:nth-child(11){animation-delay:.55s}
.lp-node:nth-child(13){animation-delay:.65s}
.lp-node:nth-child(15){animation-delay:.75s}
.lp-node:nth-child(17){animation-delay:.85s}

/* section */
.lp-section{margin-bottom:34px;}
.lp-section-head{
  display:flex;
  align-items:center;
  gap:10px;
  margin-bottom:14px;
}
.lp-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0;}
.lp-h2{
  font-family:'Space Grotesk',sans-serif;
  font-size:19px;
  font-weight:600;
  margin:0;
}

/* links grid */
.lp-links{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:10px;
}
.lp-link{
  display:flex;
  flex-direction:column;
  gap:3px;
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:10px;
  padding:12px 14px;
  text-decoration:none;
}
.lp-link-label{font-size:12px;color:var(--muted);}
.lp-link-url{font-family:'IBM Plex Mono',monospace;font-size:12.5px;color:var(--blue);word-break:break-all;}

/* endpoint table */
.lp-table{width:100%;border-collapse:collapse;font-size:14px;}
.lp-table th{
  text-align:left;
  font-family:'IBM Plex Mono',monospace;
  font-size:11px;
  letter-spacing:.08em;
  text-transform:uppercase;
  color:var(--muted);
  padding:0 12px 10px;
  border-bottom:1px solid var(--line);
}
.lp-table td{
  padding:10px 12px;
  border-bottom:1px solid var(--line);
  vertical-align:middle;
}
.lp-method{
  font-family:'IBM Plex Mono',monospace;
  font-size:11.5px;
  font-weight:600;
  padding:3px 9px;
  border-radius:999px;
  display:inline-block;
}
.lp-method.get{background:#0f3d2e;color:var(--green);}
.lp-method.post{background:#4a2a10;color:var(--orange);}
.lp-endpoint{font-family:'IBM Plex Mono',monospace;color:var(--text);}

/* cards */
.lp-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;}
.lp-card{
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:10px;
  padding:16px;
}
.lp-card-title{
  font-family:'Space Grotesk',sans-serif;
  font-weight:600;
  font-size:14.5px;
  margin:0 0 6px;
}
.lp-card-body{color:var(--muted);font-size:13.5px;line-height:1.5;margin:0;}
.lp-card-body code{font-family:'IBM Plex Mono',monospace;color:var(--yellow);font-size:12.5px;}

/* stat pills */
.lp-stats{display:flex;gap:10px;flex-wrap:wrap;}
.lp-stat{
  font-family:'IBM Plex Mono',monospace;
  font-size:13px;
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:8px;
  padding:10px 14px;
  flex:1;
  min-width:120px;
}
.lp-stat b{display:block;font-size:20px;font-family:'Space Grotesk',sans-serif;}

/* tradeoff */
.lp-tradeoff{
  background:var(--surface);
  border:1px solid var(--line);
  border-left:3px solid var(--yellow);
  border-radius:10px;
  padding:16px 18px;
  font-size:13.5px;
  color:var(--muted);
  line-height:1.6;
}
.lp-tradeoff b{color:var(--text);}

/* tech tags */
.lp-tags{display:flex;flex-wrap:wrap;gap:8px;}
.lp-tag{
  font-family:'IBM Plex Mono',monospace;
  font-size:12px;
  background:var(--surface2);
  border:1px solid var(--line);
  border-radius:6px;
  padding:6px 10px;
  color:var(--text);
}

.lp-footer{
  margin-top:44px;
  padding-top:20px;
  border-top:1px solid var(--line);
  display:flex;
  justify-content:space-between;
  align-items:center;
  flex-wrap:wrap;
  gap:10px;
  color:var(--muted);
  font-size:13px;
  font-family:'IBM Plex Mono',monospace;
}
.lp-footer a{color:var(--blue);text-decoration:none;}

@media (max-width:520px){
  .lp-h1{font-size:28px;}
  .lp-pipeline{padding:14px;}
}
</style>

<div class="lp-wrap">
  <div class="lp-inner">

    <p class="lp-eyebrow">Tech Intern Assignment</p>
    <h1 class="lp-h1">LinkPlease <span>—</span> PseudoGram Automation API</h1>
    <p class="lp-sub">Keyword-based comment-to-DM automation backend built with FastAPI, SQLite, and a background worker for delivery + retries.</p>

    <!-- pipeline hero -->
    <div class="lp-pipeline">
      <span class="lp-node g">Comment</span><span class="lp-arrow">→</span>
      <span class="lp-node b">Webhook</span><span class="lp-arrow">→</span>
      <span class="lp-node p">Verify Sig</span><span class="lp-arrow">→</span>
      <span class="lp-node o">Match Keyword</span><span class="lp-arrow">→</span>
      <span class="lp-node o">Create Job</span><span class="lp-arrow">→</span>
      <span class="lp-node b">Worker</span><span class="lp-arrow">→</span>
      <span class="lp-node g">Send DM</span><span class="lp-arrow">→</span>
      <span class="lp-node g">Delivered</span><span class="lp-arrow">/</span>
      <span class="lp-node r">Retry</span>
    </div>

    <!-- live links -->
    <div class="lp-section">
      <div class="lp-section-head"><span class="lp-dot" style="background:var(--green)"></span><h2 class="lp-h2">Live Links</h2></div>
      <div class="lp-links">
        <a class="lp-link" href="https://link-please-assignment.onrender.com/"><span class="lp-link-label">🌐 Live API</span><span class="lp-link-url">/</span></a>
        <a class="lp-link" href="https://link-please-assignment.onrender.com/docs"><span class="lp-link-label">📚 Swagger Docs</span><span class="lp-link-url">/docs</span></a>
        <a class="lp-link" href="https://link-please-assignment.onrender.com/stats"><span class="lp-link-label">📊 Live Stats</span><span class="lp-link-url">/stats</span></a>
        <a class="lp-link" href="https://link-please-assignment.onrender.com/rules"><span class="lp-link-label">📋 Rules</span><span class="lp-link-url">/rules</span></a>
        <a class="lp-link" href="https://link-please-assignment.onrender.com/events"><span class="lp-link-label">📨 Events</span><span class="lp-link-url">/events</span></a>
        <a class="lp-link" href="https://link-please-assignment.onrender.com/jobs"><span class="lp-link-label">⚙️ Jobs</span><span class="lp-link-url">/jobs</span></a>
        <a class="lp-link" href="https://github.com/dinesh5517/link-please-assignment"><span class="lp-link-label">🐙 GitHub</span><span class="lp-link-url">dinesh5517/link-please-assignment</span></a>
      </div>
    </div>

    <!-- endpoints -->
    <div class="lp-section">
      <div class="lp-section-head"><span class="lp-dot" style="background:var(--blue)"></span><h2 class="lp-h2">API Endpoints</h2></div>
      <table class="lp-table">
        <thead><tr><th>Method</th><th>Endpoint</th><th>Purpose</th></tr></thead>
        <tbody>
          <tr><td><span class="lp-method get">GET</span></td><td class="lp-endpoint">/</td><td>Health check</td></tr>
          <tr><td><span class="lp-method post">POST</span></td><td class="lp-endpoint">/rules</td><td>Create rule</td></tr>
          <tr><td><span class="lp-method get">GET</span></td><td class="lp-endpoint">/rules</td><td>List rules</td></tr>
          <tr><td><span class="lp-method post">POST</span></td><td class="lp-endpoint">/webhook</td><td>Receive webhook</td></tr>
          <tr><td><span class="lp-method get">GET</span></td><td class="lp-endpoint">/stats</td><td>View statistics</td></tr>
          <tr><td><span class="lp-method get">GET</span></td><td class="lp-endpoint">/events</td><td>View events</td></tr>
          <tr><td><span class="lp-method get">GET</span></td><td class="lp-endpoint">/jobs</td><td>View DM jobs</td></tr>
          <tr><td><span class="lp-method get">GET</span></td><td class="lp-endpoint">/jobs/{job_id}</td><td>View one job</td></tr>
        </tbody>
      </table>
    </div>

    <!-- security & dedup -->
    <div class="lp-section">
      <div class="lp-section-head"><span class="lp-dot" style="background:var(--purple)"></span><h2 class="lp-h2">Security & Deduplication</h2></div>
      <div class="lp-cards">
        <div class="lp-card">
          <p class="lp-card-title">🔐 Webhook Signature</p>
          <p class="lp-card-body">Verified via <code>HMAC-SHA256(raw_body, API_KEY)</code> against the <code>X-PseudoGram-Signature</code> header. Bad signature → <code>401 Unauthorized</code>.</p>
        </div>
        <div class="lp-card">
          <p class="lp-card-title">🔄 Duplicate Events</p>
          <p class="lp-card-body">Every webhook carries an <code>event_id</code>. Repeats are stored and ignored, returning <code>duplicate event ignored</code>.</p>
        </div>
        <div class="lp-card">
          <p class="lp-card-title">🛡️ Duplicate DMs</p>
          <p class="lp-card-body">The pair <code>(user_id + rule_id)</code> is protected at the database level — the same user can't get the same rule's DM twice.</p>
        </div>
        <div class="lp-card">
          <p class="lp-card-title">🗑️ Deleted Comments</p>
          <p class="lp-card-body">On <code>comment.deleted</code>, a still-queued job is cancelled. A DM already sent to the external API can't be recalled.</p>
        </div>
      </div>
    </div>

    <!-- reconciliation -->
    <div class="lp-section">
      <div class="lp-section-head"><span class="lp-dot" style="background:var(--orange)"></span><h2 class="lp-h2">Delivery Reconciliation</h2></div>
      <div class="lp-cards">
        <div class="lp-card">
          <p class="lp-card-title">♻️ Status Check</p>
          <p class="lp-card-body">A <code>202 Accepted</code> doesn't mean delivered. The worker checks status, retrying failed sends up to <b style="color:var(--text)">3 times</b> to prevent silent message loss.</p>
        </div>
        <div class="lp-card">
          <p class="lp-card-title">🚦 Rate Limiting</p>
          <p class="lp-card-body">Sliding-window limiter allows <code>10 DMs / 60s</code>, and the worker backs off automatically on upstream rate-limit responses.</p>
        </div>
      </div>
    </div>

    <!-- stats example -->
    <div class="lp-section">
      <div class="lp-section-head"><span class="lp-dot" style="background:var(--green)"></span><h2 class="lp-h2">Example /stats Response</h2></div>
      <div class="lp-stats">
        <div class="lp-stat" style="color:var(--green)">sent<b>1</b></div>
        <div class="lp-stat" style="color:var(--red)">failed<b>0</b></div>
        <div class="lp-stat" style="color:var(--blue)">queued<b>0</b></div>
        <div class="lp-stat" style="color:var(--purple)">duplicates_blocked<b>0</b></div>
      </div>
    </div>

    <!-- tradeoff -->
    <div class="lp-section">
      <div class="lp-section-head"><span class="lp-dot" style="background:var(--yellow)"></span><h2 class="lp-h2">Main Tradeoff</h2></div>
      <div class="lp-tradeoff">
        <b>Now:</b> the rate limiter keeps timestamps in memory — simple, fast, no extra service, but a restart clears them.<br>
        <b>Later:</b> move to Redis for a persistent, distributed rate limiter.
      </div>
    </div>

    <!-- tech stack -->
    <div class="lp-section">
      <div class="lp-section-head"><span class="lp-dot" style="background:var(--blue)"></span><h2 class="lp-h2">Tech Stack</h2></div>
      <div class="lp-tags">
        <span class="lp-tag">🐍 Python</span>
        <span class="lp-tag">⚡ FastAPI</span>
        <span class="lp-tag">🧩 Pydantic</span>
        <span class="lp-tag">🗄️ SQLite</span>
        <span class="lp-tag">🧱 SQLAlchemy</span>
        <span class="lp-tag">🔐 HMAC-SHA256</span>
        <span class="lp-tag">☁️ Render</span>
        <span class="lp-tag">🐙 GitHub</span>
      </div>
    </div>

    <div class="lp-footer">
      <span>by Dinesh</span>
      <a href="https://github.com/dinesh5517/link-please-assignment">github.com/dinesh5517/link-please-assignment</a>
    </div>

  </div>
</div>
