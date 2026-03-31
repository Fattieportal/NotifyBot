# 🚀 Deployment Guide - Auto Notify Web App

## Quick Start (Local Development)

### 1. Installeer Dependencies

```powershell
# Navigeer naar web-app directory
cd "c:\Users\Gslik\Notify bot\web-app"

# Run de setup script (installeert alles automatisch)
.\setup-webapp.ps1
```

Dit installeert:
- ✅ Next.js 14 frontend packages
- ✅ Python FastAPI backend dependencies  
- ✅ Kopieert alle scrapers van je originele bot
- ✅ Maakt virtual environment aan
- ✅ Kopieert .env configuratie

### 2. Start Development Server

```powershell
# Gebruik de automatisch gegenereerde dev script
.\dev.ps1
```

Of handmatig:

```powershell
# Terminal 1: Backend (FastAPI)
cd api
..\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (Next.js)  
cd frontend
npm run dev
```

Open browser: **http://localhost:3000**

---

## 🌐 Vercel Deployment (Production)

### Vereisten
- GitHub account
- Vercel account (gratis: https://vercel.com)
- PostgreSQL database (aanbevolen: Vercel Postgres)

### Stap 1: Push naar GitHub

```powershell
cd "c:\Users\Gslik\Notify bot"

# Initialiseer Git repository
git init
git add .
git commit -m "Initial commit: Auto Notify Web App"

# Create GitHub repo en push
# Ga naar https://github.com/new
# Maak nieuwe repository aan (bijv. "auto-notify-bot")
# Volg de instructies om te pushen
git remote add origin https://github.com/YOUR_USERNAME/auto-notify-bot.git
git branch -M main
git push -u origin main
```

### Stap 2: Deploy naar Vercel

#### Via Vercel Dashboard (Aanbevolen)

1. **Login bij Vercel**: https://vercel.com/login
2. **Import Project**: 
   - Click "Add New..." → "Project"
   - Select je GitHub repository
3. **Configure Project**:
   ```
   Root Directory: web-app
   Framework Preset: Next.js
   Build Command: cd frontend && npm run build
   Output Directory: frontend/.next
   ```

4. **Environment Variables**:
   Voeg toe in Vercel dashboard:
   ```
   TELEGRAM_BOT_TOKEN=8133422783:AAFQJGiAmTSgbfCxHCHG3IbldzLF2j5Ab-g
   TELEGRAM_CHAT_ID=716446644
   
   # Optional: Discord
   DISCORD_WEBHOOK_URL=your_discord_webhook
   
   # Optional: Email
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_USERNAME=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_TO=recipient@example.com
   
   # Database (zie Stap 3)
   DATABASE_URL=postgresql://...
   ```

5. **Deploy**: Click "Deploy"

#### Via Vercel CLI

```powershell
# Installeer Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd "c:\Users\Gslik\Notify bot\web-app"
vercel --prod
```

### Stap 3: Database Setup (PostgreSQL)

#### Option A: Vercel Postgres (Aanbevolen - Gratis Tier)

1. Ga naar je project in Vercel Dashboard
2. Click "Storage" tab → "Create Database"
3. Select "Postgres" → "Continue"
4. Vercel maakt automatisch `DATABASE_URL` environment variable aan
5. Database schema wordt automatisch aangemaakt bij eerste API call

#### Option B: Externe PostgreSQL (Railway, Supabase, etc.)

```powershell
# Railway (gratis $5/maand credit)
# 1. Ga naar https://railway.app
# 2. Create nieuwe PostgreSQL database
# 3. Kopieer Connection String
# 4. Voeg toe als DATABASE_URL in Vercel

# Supabase (gratis tier)
# 1. Ga naar https://supabase.com
# 2. Create nieuw project
# 3. Kopieer PostgreSQL connection string
# 4. Voeg toe als DATABASE_URL in Vercel
```

### Stap 4: Database Schema

De database schema wordt automatisch aangemaakt. Voor handmatige setup:

```sql
CREATE TABLE IF NOT EXISTS listings (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    listing_id VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    price VARCHAR(100),
    location TEXT,
    url TEXT NOT NULL,
    image_url TEXT,
    content_hash VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, listing_id)
);

CREATE INDEX idx_platform ON listings(platform);
CREATE INDEX idx_created_at ON listings(created_at);
CREATE INDEX idx_content_hash ON listings(content_hash);
```

---

## 📊 Productie Monitoring

### Vercel Dashboard Functies

1. **Analytics**: Real-time traffic statistics
2. **Logs**: API request logs en errors
3. **Performance**: Response times en Core Web Vitals
4. **Deployments**: Git-based deployment history

### Scheduled Scraping

Vercel heeft **geen background tasks** voor gratis tier. Voor scheduled scraping:

#### Option 1: Vercel Cron Jobs (Pro Plan - $20/maand)

Voeg toe aan `vercel.json`:
```json
{
  "crons": [{
    "path": "/api/scrape/all",
    "schedule": "0 */4 * * *"
  }]
}
```

#### Option 2: External Cron Service (GRATIS)

**EasyCron** (https://www.easycron.com - gratis tier):
```
1. Create account
2. Add cron job:
   URL: https://your-app.vercel.app/api/scrape/all
   Schedule: Every 4 hours
   Method: POST
```

**Cron-job.org** (https://cron-job.org):
```
1. Create account
2. Add nieuwe cron:
   URL: https://your-app.vercel.app/api/scrape/all
   Interval: 0 */4 * * *
```

#### Option 3: GitHub Actions (GRATIS)

Maak `.github/workflows/scheduled-scrape.yml`:
```yaml
name: Scheduled Scraping
on:
  schedule:
    - cron: '0 */4 * * *'  # Elke 4 uur
  workflow_dispatch:  # Manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Scrape
        run: |
          curl -X POST https://your-app.vercel.app/api/scrape/all \
            -H "Content-Type: application/json"
```

---

## 🔧 Post-Deployment Setup

### 1. Test Notification Systeem

Ga naar je live app → **Notifications tab**:
1. Voer Telegram credentials in
2. Click "Send Test Message"
3. Bevestig ontvangst in Telegram

### 2. Configureer Platforms

Ga naar **Configure Platforms tab**:
1. Select platform (bijv. Marktplaats)
2. Vul zoekcriteria in:
   - Zoekterm: "BMW 3 serie"
   - Prijs min: 5000
   - Prijs max: 15000
   - Postcode: 1000
3. Click **Test Scrape** → Controleer resultaten
4. Click **Save Configuration**

### 3. Setup Scheduled Scraping

Kies één van de Cron options hierboven en test:
```powershell
# Test manual scrape via API
curl -X POST https://your-app.vercel.app/api/scrape/all
```

---

## 🛡️ Security Best Practices

### Environment Variables

❌ **NOOIT** commit naar Git:
- API tokens
- Database credentials  
- Email passwords

✅ **Gebruik** Vercel Environment Variables voor:
- `TELEGRAM_BOT_TOKEN`
- `DATABASE_URL`
- Alle gevoelige data

### API Rate Limiting

De app heeft al ingebouwde rate limiting:
- 1 request per 2 seconden per platform
- Exponential backoff bij blocking
- User-Agent rotation

### Database Cleanup

Automatische cleanup van oude listings (>30 dagen):
```python
# Gebeurt automatisch in DatabaseManager
# Zie database/db_manager.py
```

---

## 📈 Scaling

### Gratis Tier Limieten (Vercel)

- **Function Executions**: 100GB-Hrs/maand
- **Bandwidth**: 100GB/maand
- **API Requests**: Unlimited (met rate limiting)

Dit is **ruim voldoende** voor:
- 5 platforms scrapen elke 4 uur
- 1000+ listings per maand
- Real-time notifications

### Upgrade Opties

Als je meer nodig hebt:

**Vercel Pro ($20/maand)**:
- Cron Jobs (scheduled functions)
- Meer compute time
- Priority support

**Database Scaling**:
- Vercel Postgres Pro: $10/maand
- Railway: $5-20/maand
- Supabase Pro: $25/maand

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Oplossing**:
```powershell
cd web-app/frontend
npm install
```

### Issue: FastAPI niet bereikbaar

**Oplossing**:
```powershell
cd web-app/api
pip install -r requirements.txt
python main.py  # Test direct
```

### Issue: Database connection errors

**Oplossing**:
1. Check `DATABASE_URL` in Vercel dashboard
2. Test connection:
   ```python
   import psycopg2
   conn = psycopg2.connect(DATABASE_URL)
   print("Connected!")
   ```

### Issue: Scrapers return 0 results

**Oplossing**:
1. Ga naar **Configure Platforms**
2. Select platform
3. Click **Test Scrape**
4. Check browser console voor errors
5. HTML selectors mogelijk verouderd → Update in `scrapers/` folder

### Issue: Telegram notifications niet ontvangen

**Oplossing**:
1. Check Bot Token is correct
2. Check Chat ID is correct
3. Stuur `/start` naar je bot
4. Test via web UI: **Notifications → Send Test Message**

---

## 📚 Volgende Stappen

1. ✅ **Deploy naar Vercel** (volg Stap 1-4 hierboven)
2. ✅ **Setup Database** (Vercel Postgres aanbevolen)
3. ✅ **Configureer Platforms** (via web UI)
4. ✅ **Test Notifications** (Telegram test message)
5. ✅ **Setup Cron Job** (GitHub Actions of EasyCron)
6. ✅ **Monitor** (Vercel Dashboard)

---

## 🎯 Live URL Voorbeeld

Na deployment krijg je:
```
https://auto-notify-bot.vercel.app
```

API endpoints:
```
GET  https://auto-notify-bot.vercel.app/api/platforms
POST https://auto-notify-bot.vercel.app/api/scrape/test
GET  https://auto-notify-bot.vercel.app/api/listings
POST https://auto-notify-bot.vercel.app/api/scrape/all
```

---

## 💡 Tips voor Productie

1. **Monitoring**: Enable Vercel Analytics voor traffic insights
2. **Errors**: Check Vercel Logs bij issues
3. **Updates**: Push naar GitHub → Vercel deploy automatisch
4. **Backup**: Download database periodiek:
   ```bash
   pg_dump $DATABASE_URL > backup.sql
   ```
5. **Performance**: Gebruik Vercel Edge Functions voor snellere responses

---

## 🆘 Support

**Issues met deployment?**
1. Check Vercel deployment logs
2. Test locally eerst: `npm run dev`
3. Verify environment variables
4. Check database connectivity

**Scraper issues?**
- Websites veranderen HTML → Update selectors in `scrapers/`
- Use "Test Scrape" button in web UI
- Check browser console voor details

---

**Veel succes met je deployment! 🚀**
