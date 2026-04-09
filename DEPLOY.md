# Telegram Mini App - Deployment Guide

## Overview

This Mini App sends queries to a Telegram bot and displays responses in real-time.

**Components:**
- `index.html` — Frontend (hosted on GitHub Pages)
- `backend.py` — Backend server (processes queries, forwards to bot)
- `bot_patch.py` — Updates to your main bot (optional, for `/menu` button)

---

## Quick Start

### 1. Deploy Backend (Choose One)

#### Option A: Deploy to Railway (Recommended, 1 min)

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub"**
3. Create a GitHub repo with these files:
   - `backend.py`
   - `requirements.txt`
   - `Procfile` (content: `web: gunicorn backend:app`)
4. Connect your repo to Railway
5. Railway auto-detects Python and deploys
6. Copy the generated URL (e.g., `https://your-project.railway.app`)

#### Option B: Deploy to Heroku

1. Go to [heroku.com](https://heroku.com)
2. Click **"New"** → **"Create new app"**
3. Connect your GitHub repo (with files above + `Procfile`)
4. Click **"Deploy Branch"**
5. Copy the app URL

#### Option C: Run Locally (for testing)

```bash
pip install -r requirements.txt
python backend.py
```

Server runs on `http://localhost:5000`

---

### 2. Update Mini App with Backend URL

In `index.html`, find this line (~line 215):

```javascript
const BACKEND_URL = "http://localhost:5000";  // Change this
```

Replace with your deployed URL:

```javascript
const BACKEND_URL = "https://your-railway-app.railway.app";
```

Then **push to GitHub** — GitHub Pages will auto-rebuild.

---

### 3. Update Bot with Menu Button (Optional)

If you want a persistent "Open Query Panel" button in your bot:

1. Open **@BotFather** in Telegram
2. Select your bot → **Bot Settings** → **Menu Button**
3. Set URL to: `https://greatday250401-netizen.github.io/telegram-miniapp/`
4. Type: **Web App**

Now users can tap the button to open the Mini App without typing `/menu`.

---

## How It Works

```
User clicks "Send" in Mini App
         ↓
Mini App extracts query + user_id
         ↓
Mini App sends to backend: POST /query {query, user_id}
         ↓
Backend forwards to bot via Telegram Bot API
         ↓
Bot receives and user types/bot auto-responds in chat
         ↓
Backend polls for response using getUpdates
         ↓
Backend returns response to Mini App
         ↓
Mini App displays response
```

---

## Troubleshooting

**"Connection error"**
- Check `BACKEND_URL` is correct in index.html
- Ensure backend is running and accessible
- Check browser console for CORS errors

**"No response from bot (timeout)"**
- Backend waited 10 seconds for bot to respond
- Make sure your bot is handling the query properly
- Bot must send a reply message in the chat (same user)

**Backend crashes**
- Check logs in Railway/Heroku dashboard
- Ensure `BOT_TOKEN` in `backend.py` is correct
- Check Python version compatibility

---

## Configuration

**In `backend.py`:**
- `BOT_TOKEN` — Your Telegram bot token
- `POLL_TIMEOUT` — Seconds to wait for bot response (default: 10)
- `POLL_INTERVAL` — How often to check for updates (default: 0.5s)

**In `index.html`:**
- `REPORTS` — Query types (S1, Laystars, Fairenter)
- `PERIODS` — Time periods
- `FILTERS` — Sport categories
- `MARKETS` — Market types

---

## Notes

- The Mini App uses Telegram's Web App API to extract the user ID
- Responses are polled from the bot's message stream
- History is stored in-memory (clears on page reload)
- CORS is enabled for frontend ↔ backend communication

---

## Support

If issues arise:
1. Check backend logs (Railway/Heroku dashboard)
2. Verify bot token is correct
3. Test bot manually in Telegram to ensure it responds
4. Check browser console for JavaScript errors
