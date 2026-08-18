# ROADMAP — mkh.learningIGuploadatmn (2nd IG account automation)

Ye file naye Claude chat ko sirf **paste/attach** kar dena — poora context ismein hai,
kuch bhi dobara explain karne ki zaroorat nahi.

---

## 🧾 Background (context, taaki naya Claude bhi samajh jaye)

- Maine (user) pehle se ek working automation banaya hua hai (`staticurdureel` repo) jo
  Google Drive → Instagram Reels ka pura pipeline handle karta hai: Drive folder me reel
  daalo → automation khud download/validate/schedule/publish karta hai, **hourly basis** pe,
  GitHub Actions ke through (cron `5 * * * *`).
- Timing bilkul sahi/precise ho, is ke liye **cron-job.org** bhi use kiya tha (external cron
  ping service) — GitHub Actions ka apna schedule kabhi kabhi 5-15 min late/skip ho sakta hai,
  to cron-job.org se `workflow_dispatch` API endpoint ko hit karke run trigger kiya jata hai
  taaki timing accurate rahe. (Agar naye repo me bhi yahi chahiye to isi tarah cron-job.org
  pe ek naya monitor is naye repo ke liye alag se banana hoga — GitHub token wahi ho sakta hai,
  bas target repo/workflow naya hoga.)
- Ab **dusra Instagram account** ke liye same automation chahiye, **different reels ke
  saath**, isi tarah hourly automated — bas Drive folder alag, IG account alag.
- Decision ho chuka hai: **sirf rename se kaam nahi chalega** — code me `account_id` sirf
  label hai, database/queue/scheduler/publisher kahin bhi is se filter nahi karte. Isliye
  ek **alag duplicate copy** banai gayi hai (naya repo banega), same logic, alag config.

---

## ✅ Ab tak kya ho chuka hai (is zip me already done)

1. Poora `staticurdureel` project duplicate kiya gaya — naya folder/project naam:
   **`mkh.learningIGuploadatmn`**
2. `config.py` me `account_id` update kar diya gaya → `"makhmoor.learing"`
   (sirf logging/identification ke liye, taaki dono account ke logs/runs clearly alag
   pehchane ja sakein).
3. `user_config.json` reset kar diya gaya (placeholder values ke saath) — purani wali
   `drive_folder_id` / `ig_user_id` (pehle account ki) hata di gayi hai:
   ```json
   {
     "drive_folder_id": "PUT_NEW_DRIVE_FOLDER_ID_HERE",
     "ig_user_id": "PUT_NEW_IG_BUSINESS_ACCOUNT_ID_HERE",
     "max_reels_this_run": 1
   }
   ```
4. `database/instagram.db` — bilkul fresh/empty banayi gayi hai (sahi schema ke saath:
   `reels`, `run_log`, `app_state` tables) — purane account ka koi data isme nahi hai.
5. `database/drive_sync_state.json` reset kar diya gaya (`downloaded_ids: []`) taaki ye
   naya automation apne naye Drive folder ko processing samjhe, purane folder ki files
   dobara download na kare.
6. Purane account ke secrets/credentials **hata diye gaye hain** (security ke liye):
   `credentials.json` (Google service account) aur `token.json` (Meta access token) —
   ye dono naye account ke liye **naye banane honge** (steps neeche).
7. Purane logs/`__pycache__`/`.git` history hata di gayi — clean slate.
8. `COMMANDS.md` ke references naye project name ke hisaab se update kar diye gaye.
9. `.github/workflows/pipeline.yml` aur `token_refresh.yml` — **as-is copy hain**, koi
   change nahi kiya gaya kyunki inki logic already generic hai (sab kuch GitHub Secrets
   se aata hai) — bas naye repo me naye Secrets set karne honge (neeche list hai).

**Ye is zip ke andar already tayyar hai — koi code likhne ki zaroorat nahi bachi.**

---

## ⏭️ Ab kya karna hai (baaqi steps — in order se karo)

### Step 1 — Naya GitHub repo banao
- GitHub pe naya empty repo banao (e.g. `mkh.learningIGuploadatmn`).
- Is `mkh.learningIGuploadatmn` folder (jo is zip me hai) ko us naye repo me push karo:
  ```powershell
  cd D:\mkh.learningIGuploadatmn
  git init
  git remote add origin https://github.com/<username>/mkh.learningIGuploadatmn.git
  git add .
  git commit -m "Initial setup - second IG account pipeline"
  git branch -M main
  git push -u origin main
  ```

### Step 2 — Naya Google Drive folder
- Ek naya Google Drive folder banao (isi me naye reels daaloge).
- Folder ka ID copy karo (URL se — `.../folders/<ID>`).
- `user_config.json` me `drive_folder_id` field me ye ID daal do.

### Step 3 — Google service account access
- Same service account (jo `credentials.json` me tha, agar reuse karna hai) ko is naye
  Drive folder par "Viewer" access do — **ya** naya service account bhi bana sakte ho
  Google Cloud Console se. Jo bhi credentials.json use karoge, uska content GitHub Secret
  `GOOGLE_SERVICE_ACCOUNT_JSON` me jayega (Step 6 me).

### Step 4 — Dusra Instagram professional/business account
- Confirm karo ke dusra IG account **Professional/Business** account hai aur ek
  **Facebook Page** se linked hai (Graph API requirement).
- Us Page/IG account ki **IG User ID** nikaalo (Graph API Explorer ya
  `GET /me/accounts` → `instagram_business_account.id`).
- `user_config.json` me `ig_user_id` field me ye ID daal do.

### Step 5 — Naya long-lived Meta access token
- `get_long_lived_token.py` wala process follow karo (jo pehle account ke liye kiya tha),
  is baar dusre IG account/app ke liye — token generate karo.
- Ye token GitHub Secret `META_ACCESS_TOKEN` me jayega.
- Agar same Meta App use kar rahe ho (App ID/Secret same), to `META_APP_ID` /
  `META_APP_SECRET` same reh sakte hain — sirf token account-specific hoga.
  Agar naya Meta App banaya hai to uske ID/Secret bhi alag honge.

### Step 6 — Naye repo me GitHub Secrets set karo
Repo → Settings → Secrets and variables → Actions → naya secret, ye sab add karo:
- `GOOGLE_SERVICE_ACCOUNT_JSON` (Step 3 wala credentials.json ka pura content)
- `META_ACCESS_TOKEN` (Step 5 wala token)
- `DRIVE_FOLDER_ID` (Step 2 wala folder ID)
- `IG_USER_ID` (Step 4 wala ID)
- `META_APP_ID`, `META_APP_SECRET` (same ya naya, Step 5 dekho)
- `SUPABASE_URL`, `SUPABASE_KEY` (agar `hosting_mode: supabase` use kar rahe ho — same
  Supabase project bhi reuse kar sakte ho, bas dusra bucket/folder use karo taaki files
  mix na ho; ya naya Supabase project bhi bana sakte ho)

### Step 7 — Test run
- Repo ke Actions tab se `pipeline.yml` ko manually trigger karo
  (`workflow_dispatch` button, ya `gh workflow run pipeline.yml`).
- `max_reels_this_run: 1` already set hai (safe test ke liye) — 1-2 reels Drive folder
  me daal ke dekho ke pura flow (sync → schedule → publish) sahi chal raha hai.
- `python show_all.py` se status check karo.

### Step 8 — cron-job.org (agar precise timing chahiye, jaisa pehle wale account me kiya tha)
- cron-job.org pe naya monitor/job banao jo is naye repo ke
  `workflow_dispatch` API endpoint ko hit kare (GitHub token ke saath), hourly.
- Ye optional hai — GitHub Actions ka apna `cron: "5 * * * *"` already hourly chalega;
  cron-job.org sirf timing ko aur precise/reliable banane ke liye extra layer hai.

### Step 9 — Scale up
- Test successful hone ke baad `max_reels_this_run` ko `user_config.json` me
  bada kar do (ya hata do) taaki bulk reels process ho sakein.
- Ab bas naye Drive folder me reels daalte raho — baaqi sab automatic hoga, hourly.

---

## 📌 Important notes / gotchas

- **Dono automation completely independent hain** — alag repo, alag secrets, alag
  database, alag Drive folder. Ek automation ka run dusre ko touch nahi karega.
- Dono account milake bhi Meta ke rate limit (~25 posts/24h **per IG account**) ke
  andar rahenge — ye limit per-account hai, to koi conflict nahi hoga.
- Agar `hosting_mode: supabase` same Supabase project reuse kar rahe ho, to
  `supabase_bucket` field `user_config.json` me alag rakhna (e.g. `"reels2"`) taaki
  dono account ki video files mix na ho.
- Purane account (`staticurdureel`) me kuch bhi change nahi karna — wo waise hi chalta
  rahega, independently.

---

## 🗣️ Agar chat limit aane par naye Claude ko batana ho

Bas ye line kaafi hai:
> "Ye mera ROADMAP.md hai — is zip me sab kuch tayyar hai, [Step X] tak ho chuka hai,
> ab [Step Y] se aage help karo."

Aur upar wala "✅ Ab tak kya ho chuka hai" section update karte rehna jaise-jaise
steps complete karte jao, taaki agla Claude turant pick kar sake.
