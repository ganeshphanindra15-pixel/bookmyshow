# 🚀 Deploy Myntra Size Monitor to Railway — Step by Step

---

## What you need before starting
- A **GitHub account** (free) → https://github.com
- A **Railway account** (free) → https://railway.app
- Your **Telegram Bot Token** (from @BotFather)
- Your **Telegram Chat ID** (from @userinfobot)

---

## Step 1 — Create a GitHub Repository

1. Go to https://github.com and log in
2. Click the **+** icon (top right) → **New repository**
3. Name it: `myntra-size-monitor`
4. Set it to **Private**
5. Click **Create repository**

---

## Step 2 — Upload your files to GitHub

Upload these 3 files to the repository:
- `myntra_size_monitor.py`
- `requirements.txt`
- `Dockerfile`

To upload:
1. On your new repo page, click **Add file** → **Upload files**
2. Drag and drop all 3 files
3. Click **Commit changes**

---

## Step 3 — Sign up on Railway

1. Go to https://railway.app
2. Click **Login** → **Login with GitHub**
3. Authorize Railway to access your GitHub

---

## Step 4 — Create a new Railway project

1. On Railway dashboard, click **+ New Project**
2. Select **Deploy from GitHub repo**
3. Choose your `myntra-size-monitor` repo
4. Railway will detect the Dockerfile automatically — click **Deploy Now**

---

## Step 5 — Add your secret credentials (IMPORTANT)

Your Bot Token and Chat ID must be added as **Environment Variables** — never hardcode them.

1. In your Railway project, click on the service (the box that appeared)
2. Go to the **Variables** tab
3. Click **+ New Variable** and add:

   | Name        | Value                        |
   |-------------|------------------------------|
   | `BOT_TOKEN` | your token from @BotFather   |
   | `CHAT_ID`   | your ID from @userinfobot    |

4. Railway will **automatically restart** the bot with the new variables

---

## Step 6 — Verify it's running

1. Click the **Deployments** tab in Railway
2. Click on the latest deployment → **View Logs**
3. You should see something like:

   ```
   Myntra Size Monitor started
   Product : https://www.myntra.com/28873290
   Size    : 9
   Interval: every 10 minutes
   Checking size 9 availability...
   ```

4. Check your Telegram — you should receive a status message within a minute!

---

## ✅ You're done!

The bot is now running 24/7 on Railway's servers.
You'll get a Telegram message the moment Size 9 becomes available.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| No Telegram message received | Double-check BOT_TOKEN and CHAT_ID in Railway Variables |
| Build failed | Make sure all 3 files are uploaded to GitHub |
| "No data returned from Myntra" in logs | Myntra may be blocking the request temporarily — it will retry automatically |

---

## To stop the bot
Go to Railway → your project → **Settings** → **Remove Service**

Or simply delete the project.
