# mkh.learningIGuploadatmn — Reel Pipeline Command Reference (2nd IG account)

Repo: makhmoorsaifi/mkh.learningIGuploadatmn (naya repo — jo tum banaoge)
Local: D:\mkh.learningIGuploadatmn (PowerShell)

---

## 1. DAILY / ROUTINE — Check Status

```powershell
cd D:\mkh.learningIGuploadatmn
git pull
python show_all.py
```
Shows every reel: id, filename, status (validated / scheduled / published / failed), scheduled_at, publish_timestamp.

---

## 2. ADD MORE REELS (bulk upload, e.g. 1000 videos)

Nothing to run manually — just:
1. Upload video files into the configured Google Drive folder (`DRIVE_FOLDER_ID` secret).
2. Wait for the next hourly run (cron: `5 * * * *`), OR trigger immediately:
```powershell
gh workflow run pipeline.yml
```
3. Pipeline auto-detects new files → downloads → validates → schedules into `posting_times` slots → publishes when due.

**Before doing a big bulk upload, check/adjust `config.py`:**
- `posting_times` — how many reels get scheduled per day. Add more times if you want a bigger backlog cleared faster.
- Keep total daily posts under Instagram's rate limit (~25/day per account) to avoid publish failures.

---

## 3. FORCE-PUBLISH A SPECIFIC REEL RIGHT NOW (skip its scheduled time)

### Step 1 — create the helper script (one-time, if not already in repo)
```powershell
@"
from database import get_connection
from datetime import datetime, timezone
import sys

reel_id = int(sys.argv[1])
with get_connection() as c:
    c.execute("UPDATE reels SET status='scheduled', scheduled_at=? WHERE id=?",
              (datetime.now(timezone.utc).isoformat(), reel_id))
    c.commit()
print(f"Reel {reel_id} scheduled_at set to now (UTC)")
"@ | Out-File -Encoding utf8 force_publish.py
```

### Step 2 — run it for the target reel id
```powershell
python force_publish.py <ID>
python show_all.py   # confirm scheduled_at changed
```

### Step 3 — commit & push (ALWAYS pull first to avoid conflicts)
```powershell
git pull
git add database/instagram.db force_publish.py
git commit -m "manual: force publish reel <ID> now"
git push
```

### Step 4 — trigger the workflow immediately (don't wait for hourly cron)
```powershell
gh workflow run pipeline.yml
```

### Step 5 — wait ~1-2 min, then verify
```powershell
Start-Sleep -Seconds 60
git pull
python show_all.py
```
Reel should now show `status: published` with a `publish_timestamp`.

⚠️ **Do NOT run force_publish.py on a reel that is already `published`** — it resets status back to `scheduled`, which can cause a duplicate post if a workflow run processes it again before you catch it.

---

## 4. RETRY A FAILED REEL

```powershell
python retry_failed.py
git add database/instagram.db
git commit -m "retry failed reels"
git push
gh workflow run pipeline.yml
```

## 5. RESET SCHEDULING (re-assign scheduled_at for all pending reels)

```powershell
python reset_schedule.py
git add database/instagram.db
git commit -m "reset schedule"
git push
gh workflow run pipeline.yml
```

---

## 6. CHECK TOKEN EXPIRY (Meta access token)

```powershell
gh run list --workflow="pipeline.yml" --limit 1
gh run view <RUN_ID> --log
```
Look for the "Check token expiry (temporary debug step)" output — shows `Token expires at: ...`. Should be ~60 days from when it was last set. If it shows today/tomorrow, the token secret needs to be regenerated (long-lived token from Meta Access Token Debugger → "Extend Access Token", NOT the short-lived Graph API Explorer token).

To update the token secret:
```powershell
gh secret set META_ACCESS_TOKEN
# paste the new long-lived token when prompted
```

---

## 7. WATCH / CHECK A WORKFLOW RUN

```powershell
gh run list --limit 5                     # recent runs
gh run view <RUN_ID> --log                # full log of a specific run
gh workflow run pipeline.yml               # manually trigger a run now
```
(Avoid `gh run watch` if it opens an interactive arrow-key menu you can't navigate — use `gh run view <ID> --log` instead for a straight log dump.)

---

## 8. TROUBLESHOOTING

### "Could not resolve host: github.com" on git push/pull
- Transient DNS issue. Retry the SAME command again after a few seconds.
- Check connectivity: `ping github.com`
- If it keeps failing, restart WiFi or try `ipconfig /flushdns` (run PowerShell as Administrator).

### "! [rejected] ... (fetch first)" or "(non-fast-forward)" on git push
Someone (usually the CI bot itself, via its own auto-commit step) pushed a newer commit. Always:
```powershell
git pull
```
first, THEN `git push` again. Never trigger a new workflow run before a rejected push is resolved — the workflow will just use stale/old state.

### Merge conflict in `database/instagram.db` after `git pull`
This is a binary file — git can't auto-merge it. You must pick one side:

- **To keep the REMOTE (GitHub/CI) version** (usually the safe default — it reflects real publish activity):
```powershell
git checkout --theirs database/instagram.db
git add database/instagram.db
git commit -m "resolve merge conflict - take remote db state"
```

- **To keep your LOCAL version instead** (rare — only if you're sure your local force-change hasn't been superseded):
```powershell
git checkout --ours database/instagram.db
git add database/instagram.db
git commit -m "resolve merge conflict - keep local db state"
```

After resolving, re-check `python show_all.py` before pushing to make sure no reel got its status incorrectly reset.

### Vim editor pops up unexpectedly during a merge/pull
Git wants a default merge commit message. Just:
1. Press `Esc`
2. Type `:wq`
3. Press `Enter`
This saves and exits with the default message — no need to type anything else.

### Want to discard local changes entirely and match GitHub exactly
```powershell
git fetch origin
git reset --hard origin/main
```
⚠️ This deletes any uncommitted/unpushed local changes permanently. Only use when you're sure local has nothing you need.

---

## 9. KEY FILES

| File | Purpose |
|---|---|
| `scheduler.py` | Assigns IST-aware posting slots |
| `publisher.py` | Publishes due reels to Instagram |
| `drive_sync.py` | Pulls new videos from Google Drive |
| `database.py` | SQLite connection (WAL mode) |
| `config.py` | `posting_times` and other settings |
| `token_store.py` / `token_refresh.py` | Meta token handling |
| `show_all.py` | Dump full reels table |
| `reset_schedule.py` | Reset all scheduled → validated |
| `retry_failed.py` | Reset all failed → scheduled |
| `check_token.py` | Print token expiry/app/scopes (debug only) |
| `force_publish.py` | (custom helper) force a reel's scheduled_at to now |

## GitHub Secrets in use
`DRIVE_FOLDER_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`, `IG_USER_ID`, `META_ACCESS_TOKEN`, `META_APP_ID`, `META_APP_SECRET`, `SUPABASE_KEY`, `SUPABASE_URL`

## Still pending / not yet implemented
Full Meta token auto-refresh (refresh + write back to GitHub secret automatically) — needs `token_refresh.py` wired into the workflow plus a `GH_PAT` secret with permission to update repo secrets.
