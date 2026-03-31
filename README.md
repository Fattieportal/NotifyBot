# Multi-Platform Notification Bot

Een professionele notification bot die automatisch nieuwe advertenties monitort op meerdere platforms en notificaties stuurt wanneer advertenties aan je criteria voldoen.

## Ondersteunde Platforms

- ✅ Marktplaats.nl
- ✅ AutoScout24
- ✅ Mobile.de
- ✅ Facebook Marketplace
- ✅ eBay Kleinanzeigen

## Features

- 🔍 Flexibele zoek criteria per platform
- 🔔 Multiple notificatie methodes (Email, Telegram, Discord)
- 💾 Duplicate detectie
- ⚡ Rate limiting & retry logic
- 🛡️ Anti-blocking maatregelen
- 📊 Logging en monitoring
- 🔧 Configureerbaar via YAML

## Technische Uitdagingen - Opgelost

### 1. Rate Limiting
- Random delays tussen requests (3-10 sec)
- Per-domain throttling
- Exponential backoff

### 2. IP Blocking Preventie
- User-Agent rotation
- Session management
- Cookie persistence
- Proxy support (optioneel)

### 3. CAPTCHA Handling
- Playwright browser automation
- Session cookies opslaan
- Manual intervention fallback

### 4. HTML Structure Changes
- Multiple CSS selector fallbacks
- Validation checks
- Admin alerts bij failures

### 5. Duplicate Prevention
- SQLite database
- Unique ID tracking
- Content hash comparison

## Installatie

```powershell
# Python 3.8+ vereist
python -m pip install -r requirements.txt

# Playwright browsers installeren (voor Facebook)
playwright install chromium
```

## Configuratie

Bewerk `config.yaml` met je criteria:

```yaml
platforms:
  marktplaats:
    enabled: true
    criteria:
      keywords: "bmw 320d"
      price_min: 5000
      price_max: 15000
      year_min: 2015

notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_TOKEN"
    chat_id: "YOUR_CHAT_ID"
```

## Gebruik

```powershell
# Start de bot
python main.py

# Run in background (Windows)
pythonw main.py

# Scheduled task (Windows Task Scheduler aanbevolen)
```

## Project Structuur

```
Notify bot/
├── main.py                 # Entry point
├── config.yaml            # Configuratie
├── requirements.txt       # Dependencies
├── scrapers/              # Platform-specifieke scrapers
│   ├── __init__.py
│   ├── base_scraper.py   # Base class
│   ├── marktplaats.py
│   ├── autoscout.py
│   ├── mobile_de.py
│   ├── facebook.py
│   └── ebay_kleinanzeigen.py
├── notifiers/             # Notificatie systemen
│   ├── __init__.py
│   ├── telegram.py
│   ├── email.py
│   └── discord.py
├── database/              # Database management
│   ├── __init__.py
│   └── db_manager.py
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── logger.py
│   ├── rate_limiter.py
│   └── user_agents.py
└── data/                  # Data storage
    └── listings.db
```

## License

MIT License - Voor commercieel gebruik door je klant.
