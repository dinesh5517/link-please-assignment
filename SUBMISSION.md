Submission checklist for LinkPlease assignment

- Repo: https://github.com/dinesh5517/link-please-assignment
- Deployed URL: https://link-please-assignment.onrender.com
- PSEUDOGRAM_API_KEY: must be set in Render environment variables before official run

Files included:
- app/ (code)
- run_simulation.py (helper to start grader sim and fetch truth.json)
- post_webhook_fix.py, run_browser_test.py (manual test helpers)
- FAILURES.md (known failure modes)

How to reproduce final verification locally:
1. Ensure `.env` contains `PSEUDOGRAM_API_KEY=...` in the repo root.
2. From repo root run:

```bash
python run_simulation.py 500 60
```

3. After completion, two files will be created next to the script:
- truth.json
- deployed_stats.json

4. Compare counts and paste both files to the grader.

If anything fails, open an issue or message the reviewer with `FAILURES.md` notes.
