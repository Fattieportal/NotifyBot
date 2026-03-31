# 🚗 Auto Notify - Web Application

**Professional web application voor het monitoren van auto-advertenties op 5 platforms met real-time notificaties.**

## 📊 Monitored Platforms

- 🟠 **Marktplaats.nl** - Grootste Nederlandse marktplaats
- 🔵 **AutoScout24** - Europese auto marketplace
- 🟢 **Mobile.de** - Duitse auto platform
- 🟣 **Facebook Marketplace** - Social media marktplaats
- 🟡 **eBay Kleinanzeigen** - Duitse classifieds

## ⚡ Quick Start

### Automated Setup (Recommended)

```powershell
# Run setup script (installeerd alles automatisch)
.\setup-webapp.ps1

# Start development servers (backend + frontend)
.\dev.ps1

# Open browser: http://localhost:3000
```

**That's it!** De app draait nu lokaal met:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Auto-reload bij code changes

### Manual Setup (Alternative)

```powershell
# Backend (Terminal 1)
cd api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

## 🎯 Features

### User Interface
- ✅ **Modern Dashboard** - Real-time statistics & platform status
- ✅ **Dynamic Forms** - Platform-specific configuration forms
- ✅ **Live Testing** - Test scraping before saving configuration
- ✅ **Listings View** - See all found listings with images & links
- ✅ **Notification Management** - Configure Telegram, Discord, Email
- ✅ **Responsive Design** - Works on desktop, tablet, mobile

### Technical
- ✅ **REST API** - FastAPI with 15 endpoints
- ✅ **Platform Schemas** - Dynamic form generation from backend
- ✅ **Rate Limiting** - Prevents IP blocking (1 req/2s per domain)
- ✅ **Anti-Detection** - User-Agent rotation, exponential backoff
- ✅ **Duplicate Prevention** - Content hashing in database
- ✅ **Real-time Updates** - Auto-refresh every 30 seconds
- ✅ **Error Handling** - Graceful degradation & user feedback

## 🏗️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3.4
- **State**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **HTTP**: Axios

### Backend
- **Framework**: FastAPI 0.110.0
- **Language**: Python 3.11
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Scraping**: BeautifulSoup4, Playwright, Selenium
- **Notifications**: python-telegram-bot, discord-webhook, sendgrid

### Deployment
- **Platform**: Vercel (Serverless)
- **Database**: Vercel Postgres / Neon
- **CI/CD**: Git-based automatic deployments

## 📁 Project Structure

```
web-app/
├── frontend/                           # Next.js Application
│   ├── app/
│   │   ├── page.tsx                   # 🏠 Main Dashboard
│   │   ├── layout.tsx                 # App Layout + Providers
│   │   └── globals.css                # Tailwind + Custom Styles
│   ├── components/
│   │   ├── StatsOverview.tsx          # 📊 Statistics Cards
│   │   ├── PlatformConfigurator.tsx   # 🔧 Platform Config Forms
│   │   ├── RecentListings.tsx         # 📋 Listings Table
│   │   └── NotificationSettings.tsx   # 🔔 Notification Setup
│   ├── package.json                   # Frontend dependencies
│   ├── tailwind.config.ts             # Tailwind configuration
│   ├── next.config.js                 # Next.js config (API rewrites)
│   └── tsconfig.json                  # TypeScript config
│
├── api/                                # FastAPI Backend
│   ├── main.py                        # 🚀 REST API (15 endpoints)
│   ├── requirements.txt               # Python dependencies
│   ├── scrapers/                      # Platform scrapers (copied from CLI bot)
│   │   ├── base_scraper.py           # Base class with anti-blocking
│   │   ├── marktplaats.py
│   │   ├── autoscout.py
│   │   ├── mobile_de.py
│   │   ├── facebook.py
│   │   └── ebay_kleinanzeigen.py
│   ├── database/
│   │   └── db_manager.py             # Database with duplicate detection
│   ├── notifiers/
│   │   ├── telegram.py
│   │   ├── discord.py
│   │   └── email.py
│   └── utils/
│       ├── rate_limiter.py
│       └── user_agents.py
│
├── vercel.json                         # ☁️ Vercel deployment config
├── setup-webapp.ps1                    # 🔧 Automated setup script
├── dev.ps1                             # 🚀 Dev launcher (auto-generated)
│
├── COMPLETE_SETUP_GUIDE.md             # 📖 Detailed setup docs
├── DEPLOYMENT_GUIDE.md                 # 🌐 Vercel deployment guide
├── FINAL_OVERVIEW.md                   # 📋 Complete project overview
├── UI_DESIGN_SPEC.md                   # 🎨 UI design specification
└── README.md                           # 📘 This file
```

## 🎨 UI Overview

### Dashboard Tabs

**1. Configure Platforms** 🔧
- Platform selector (5 platforms)
- Dynamic form (per platform verschillend)
- Test Scrape button (validates without saving)
- Save Configuration button

**2. Recent Listings** 📋
- Real-time listings table
- Images, titles, prices, locations
- Platform badges (color-coded)
- Direct links to original ads
- Auto-refresh every 30 seconds

**3. Notifications** 🔔
- Telegram setup (Bot Token + Chat ID)
- Discord webhook configuration
- Email SMTP settings
- Test buttons per notification type
- Toggle switches (enable/disable)

## 🔌 API Endpoints

### Platform Management
```http
GET  /api/platforms           # Get platform schemas
POST /api/config              # Save platform configuration
```

### Scraping
```http
POST /api/scrape/test         # Test scrape (doesn't save)
POST /api/scrape/all          # Full scrape (all enabled platforms)
GET  /api/scrape/status       # Get scraping status
```

### Listings
```http
GET  /api/listings            # Get recent listings
GET  /api/listings/{id}       # Get specific listing
```

### Statistics
```http
GET  /api/stats               # Get dashboard statistics
```

### Notifications
```http
POST /api/notifications/config  # Save notification settings
POST /api/notifications/test    # Test notification
```

## 🚀 Deployment

### Vercel (Recommended - Gratis Tier)

**1. Push to GitHub**
```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/auto-notify-bot.git
git push -u origin main
```

**2. Deploy to Vercel**
1. Login: https://vercel.com
2. Import GitHub repository
3. Root directory: `web-app`
4. Add environment variables:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHAT_ID=your_chat_id
   DATABASE_URL=postgresql://...
   ```
5. Deploy!

**Live URL**: `https://your-app.vercel.app`

**Zie `DEPLOYMENT_GUIDE.md` voor complete instructies.**

### Scheduled Scraping

Vercel gratis tier heeft geen cron jobs. Gebruik:

**Option 1: GitHub Actions** (gratis)
```yaml
# .github/workflows/scheduled-scrape.yml
schedule:
  - cron: '0 */4 * * *'  # Every 4 hours
```

**Option 2: EasyCron** (gratis service)
- URL: `https://your-app.vercel.app/api/scrape/all`
- Interval: Every 4 hours

## 📚 Documentation Files

| File | Description |
|------|-------------|
| `README.md` | This overview file |
| `COMPLETE_SETUP_GUIDE.md` | Detailed setup instructions |
| `DEPLOYMENT_GUIDE.md` | Vercel deployment guide |
| `FINAL_OVERVIEW.md` | Complete project summary |
| `UI_DESIGN_SPEC.md` | UI design specification |
| `PLATFORM_CRITERIA_ANALYSIS.md` | Platform-specific requirements |

## 🔧 Configuration
uvicorn main:app --reload
```

### Deployment (Vercel)
1. Connect GitHub repo to Vercel
2. Configure environment variables
3. Deploy!

Vercel automatically handles:
- Next.js frontend hosting
- Python serverless functions
- Environment variables
- SSL certificates
