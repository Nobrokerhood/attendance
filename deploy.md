# 🚀 DEPLOY GUIDE — Meet Attendance Web App on Render

---

## STEP 1 — Push to GitHub

```bash
cd ~/GENAI/meetweb

git init
git add .
git commit -m "Meet attendance web app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/meet-attendance.git
git push -u origin main
```

---

## STEP 2 — Encode credentials.json as Base64

Run this on your machine (in the meetweb folder):

```bash
base64 -w 0 credentials.json
```

Copy the long output string. You'll paste it in Render.

> On Windows PowerShell:
> ```powershell
> [Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json"))
> ```

---

## STEP 3 — Create Web Service on Render

1. Go to https://render.com → New → Web Service
2. Connect your GitHub repo (`meet-attendance`)
3. Set these settings:
   - **Name:** `meet-attendance-nbh`
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`

4. Under **Environment Variables**, add:
   | Key | Value |
   |-----|-------|
   | `GOOGLE_CREDENTIALS_B64` | (paste base64 string from Step 2) |
   | `APP_URL` | `https://meet-attendance-nbh.onrender.com` |

5. Click **Deploy**. Wait ~2 minutes.

---

## STEP 4 — Add Redirect URI in Google Cloud Console

⚠️ CRITICAL — OAuth won't work without this.

1. Go to https://console.cloud.google.com
2. APIs & Services → Credentials → your OAuth Client
3. Under **Authorized redirect URIs** → Add:
   ```
   https://meet-attendance-nbh.onrender.com/auth/callback
   ```
4. Click Save

---

## STEP 5 — Share URL with Team

Send your team this URL:
```
https://meet-attendance-nbh.onrender.com
```

Each person:
1. Enters their name (e.g. priya, ravi)
2. Clicks "Continue with Google"
3. Logs in with their @nobroker.in account
4. Sees their meetings → selects → clicks Export Excel

---

## ⚠️ FREE TIER NOTE

Render free tier **sleeps after 15 minutes** of inactivity.
First request after sleep takes ~30 seconds to wake up.

Also: token files are stored on disk. If Render restarts the service,
team members need to login again (takes 10 seconds, not a big deal).

To avoid this → upgrade to Render Starter ($7/month) which has persistent disk.

---

## 🧪 TEST LOCALLY FIRST

```bash
cd ~/GENAI/meetweb
pip install -r requirements.txt
APP_URL=http://localhost:8000 uvicorn app:app --reload
```
Open: http://localhost:8000

Add `http://localhost:8000/auth/callback` to Google Cloud redirect URIs for local testing.

---

## FILE STRUCTURE

```
meetweb/
├── app.py              ← FastAPI backend
├── templates/
│   └── index.html      ← Web UI
├── requirements.txt
├── render.yaml
└── tokens/             ← Auto-created, stores login tokens
```
