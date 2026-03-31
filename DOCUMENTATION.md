# Comprehensive documentation

## 🎯 Overzicht

Deze bot monitort automatisch 5 verschillende auto marktplaatsen en stuurt real-time notificaties wanneer nieuwe advertenties verschijnen die aan je criteria voldoen.

## 📋 Ondersteunde Platforms

| Platform | Techniek | Betrouwbaarheid | Status |
|----------|----------|-----------------|---------|
| **Marktplaats.nl** | Web Scraping | ⭐⭐⭐⭐ | ✅ Ready |
| **AutoScout24** | Web Scraping | ⭐⭐⭐⭐ | ✅ Ready |
| **Mobile.de** | Web Scraping | ⭐⭐⭐⭐ | ✅ Ready |
| **eBay Kleinanzeigen** | RSS Feed | ⭐⭐⭐⭐⭐ | ✅ Ready |
| **Facebook Marketplace** | Browser Automation | ⭐⭐⭐ | ⚠️ Experimental |

## 🔧 Technische Uitdagingen - Opgelost

### 1. Rate Limiting
**Probleem**: Websites blokkeren bij te veel requests
**Oplossing**:
- Random delays tussen requests (3-10 seconden)
- Per-domain rate limiting
- Exponential backoff bij failures
- Implementatie: `utils/rate_limiter.py`

### 2. IP Blocking
**Probleem**: Websites detecteren bots en blokkeren IP
**Oplossing**:
- User-Agent rotation (realistische browser headers)
- Session management met cookie persistence
- Proxy support (optioneel)
- Implementatie: `utils/user_agents.py`

### 3. CAPTCHA's
**Probleem**: Anti-bot systemen zoals CAPTCHA
**Oplossing**:
- Playwright browser automation (voor Facebook)
- Cookie persistence voor sessions
- Fallback mechanismen
- Implementatie: `scrapers/facebook.py`

### 4. HTML Structuur Veranderingen
**Probleem**: Websites veranderen hun HTML regelmatig
**Oplossing**:
- Multiple CSS selector fallbacks
- Graceful degradation
- Logging van failures
- Implementatie: `BaseScraper.safe_extract()`

### 5. Duplicate Detectie
**Probleem**: Zelfde advertenties worden meerdere keren gedetecteerd
**Oplossing**:
- SQLite database met unique constraints
- Content hashing voor vergelijking
- Timestamp tracking
- Implementatie: `database/db_manager.py`

## 🚀 Installatie & Setup

### Stap 1: Python Installatie
- Download Python 3.8+ van https://www.python.org/downloads/
- **Belangrijk**: Vink "Add Python to PATH" aan tijdens installatie!

### Stap 2: Bot Setup
```powershell
# Open PowerShell in de "Notify bot" folder
cd "C:\Users\Gslik\Notify bot"

# Run setup script
.\setup.ps1
```

Het setup script installeert automatisch:
- Virtual environment
- Alle Python dependencies
- Playwright browsers
- Nodige directories

### Stap 3: Configuratie

#### A. Telegram Bot Setup (Aanbevolen)
1. Open Telegram en zoek naar `@BotFather`
2. Stuur `/newbot` commando
3. Volg instructies om bot naam te kiezen
4. Kopieer de **Bot Token**
5. Start chat met je nieuwe bot
6. Krijg je Chat ID:
   - Ga naar: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Of stuur bericht naar bot en kijk in URL hierboven
   - Je Chat ID staat in het JSON response

#### B. Configuratie Files

**`.env` file** (credentials - NOOIT delen!):
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

**`config.yaml`** (zoek criteria):
```yaml
platforms:
  marktplaats:
    enabled: true
    criteria:
      keywords: "bmw 320d"
      price_min: 5000
      price_max: 15000
      year_min: 2015
      mileage_max: 150000
```

### Stap 4: Testen
```powershell
# Test notificaties
python main.py --test

# Test één scrape cycle
python main.py --once

# Toon database stats
python main.py --stats
```

### Stap 5: Run Bot
```powershell
# Met scheduling (blijft draaien)
python main.py

# Of gebruik run script
.\run.ps1
```

## 📊 Gebruik

### Commands
```powershell
# Normale mode - blijft draaien met scheduling
python main.py

# Run eenmalig
python main.py --once

# Test notificaties
python main.py --test

# Database statistieken
python main.py --stats

# Eigen config file
python main.py --config custom_config.yaml
```

### Background Execution
Om de bot in de background te draaien:

**Optie 1: PowerShell Background Job**
```powershell
Start-Job -ScriptBlock { 
    cd "C:\Users\Gslik\Notify bot"
    .\.venv\Scripts\Activate.ps1
    python main.py 
}
```

**Optie 2: Windows Task Scheduler** (Beste voor production)
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: "When I log on" of specifieke tijd
4. Action: Start a program
   - Program: `C:\Users\Gslik\Notify bot\.venv\Scripts\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\Users\Gslik\Notify bot`

**Optie 3: pythonw (geen console window)**
```powershell
.\.venv\Scripts\pythonw.exe main.py
```

## 🎨 Criteria Configuratie

### Marktplaats.nl
```yaml
marktplaats:
  enabled: true
  criteria:
    keywords: ["bmw 320d", "audi a4"]  # Of enkele string
    price_min: 5000
    price_max: 15000
    year_min: 2015
    year_max: 2022
    mileage_max: 150000
    postcode: "1012"  # Optioneel
    distance_km: 50   # Optioneel
```

### AutoScout24
```yaml
autoscout:
  enabled: true
  criteria:
    make: "BMW"
    model: "3 Series"
    price_min: 5000
    price_max: 15000
    year_min: 2015
    fuel_type: "Diesel"  # Diesel, Petrol, Electric, Hybrid
```

### Mobile.de
```yaml
mobile_de:
  enabled: true
  criteria:
    make: "BMW"
    model: "320"
    price_min: 5000
    price_max: 15000
    year_min: 2015
    zip_code: "10115"  # Duitse postcode
    radius_km: 100
```

### eBay Kleinanzeigen
```yaml
ebay_kleinanzeigen:
  enabled: true
  criteria:
    keywords: "bmw 320d"
    category: "216"  # 216 = Auto's
    price_min: 5000
    price_max: 15000
    zip_code: "10115"  # Optioneel
```

### Facebook Marketplace (Experimental)
```yaml
facebook:
  enabled: false  # Gebruik met voorzichtigheid!
  credentials:
    email: "je@email.com"
    password: "wachtwoord"  # Beter in .env
  criteria:
    query: "BMW 320d"
    price_min: 5000
    price_max: 15000
    location: "Amsterdam"
```

**⚠️ Facebook Waarschuwing**: 
- Vereist inloggen
- Kan account blokkeren bij overmatig gebruik
- Gebruik op eigen risico
- Overweeg officiële Facebook Graph API voor production

## 📈 Monitoring & Logs

### Log Files
- Locatie: `logs/bot.log`
- Bevat: Alle activiteit, errors, statistieken
- Colored console output voor real-time monitoring

### Database
- Locatie: `data/listings.db`
- SQLite database
- Bekijk met: DB Browser for SQLite (gratis tool)

### Statistieken
```powershell
python main.py --stats
```
Output:
```
📊 DATABASE STATISTIEKEN
============================================================
Totaal advertenties: 127
Laatste 24 uur: 15
Genotificeerd: 120
Pending: 7

Per platform:
  - marktplaats: 45
  - autoscout: 38
  - ebay_kleinanzeigen: 44
============================================================
```

## 🛠️ Troubleshooting

### "Module not found" errors
```powershell
# Activeer virtual environment
.\.venv\Scripts\Activate.ps1

# Herinstalleer dependencies
pip install -r requirements.txt
```

### Playwright browser errors
```powershell
# Reinstall browsers
playwright install chromium
```

### "No listings found"
- Check of URL correct gebouwd wordt (zie logs)
- Test URL handmatig in browser
- Website structuur kan veranderd zijn
- Check rate limiting messages in logs

### Notificaties worden niet verstuurd
```powershell
# Test notificatie systeem
python main.py --test
```
- Controleer `.env` file credentials
- Check logs voor error messages
- Test Telegram bot handmatig

### Rate limiting / IP blocking
- Verhoog delays in `config.yaml`:
  ```yaml
  anti_detection:
    random_delay_min: 5  # Verhoog van 3
    random_delay_max: 15  # Verhoog van 10
  ```
- Gebruik proxy (optioneel)

## 🔒 Security & Privacy

### Credentials Opslag
- **NOOIT** credentials in `config.yaml`
- Gebruik `.env` file voor secrets
- `.env` staat in `.gitignore`
- Voor production: Gebruik environment variables of secrets manager

### Cookies & Sessions
- Opgeslagen in `cookies/` directory
- Facebook cookies voor session persistence
- Automatisch cleanup bij logout

### Proxy Support (Optioneel)
```yaml
global:
  use_proxy: true
  proxy_url: "http://proxy:8080"
```

## 📝 Voor Je Klant

### Deployment Checklist
- [ ] Python 3.8+ geïnstalleerd
- [ ] Dependencies geïnstalleerd (`.\setup.ps1`)
- [ ] `.env` file geconfigureerd met credentials
- [ ] `config.yaml` aangepast met zoek criteria
- [ ] Test uitgevoerd (`python main.py --test`)
- [ ] Windows Task Scheduler ingesteld voor autostart
- [ ] Logs locatie gecommuniceerd

### Onderhoud
- **Dagelijks**: Check notificaties werken
- **Wekelijks**: Check logs voor errors
- **Maandelijks**: Database cleanup gebeurt automatisch
- **Bij problemen**: Check logs in `logs/bot.log`

### Kosten
- **Software**: Gratis / Open Source
- **Hosting**: Lokaal op Windows PC (gratis)
- **Telegram**: Gratis
- **Proxy** (optioneel): €5-20/maand

### Licentie
- MIT License
- Vrij te gebruiken voor commerciële doeleinden
- Geen garanties op 100% uptime (websites kunnen blokkeren)

## 🆘 Support

Voor vragen of problemen:
1. Check logs: `logs/bot.log`
2. Run diagnostics: `python main.py --stats`
3. Test notificaties: `python main.py --test`
4. Check deze documentatie

## 📚 Technische Details

### Architectuur
```
main.py                 # Entry point & orchestration
├── scrapers/          # Platform-specific scrapers
│   ├── base_scraper.py    # Shared functionality
│   ├── marktplaats.py
│   ├── autoscout.py
│   ├── mobile_de.py
│   ├── facebook.py
│   └── ebay_kleinanzeigen.py
├── notifiers/         # Notification systems
│   ├── telegram.py
│   ├── discord.py
│   └── email.py
├── database/          # Data persistence
│   └── db_manager.py
└── utils/             # Utilities
    ├── rate_limiter.py
    ├── user_agents.py
    └── logger.py
```

### Dependencies
- **requests**: HTTP requests
- **beautifulsoup4**: HTML parsing
- **playwright**: Browser automation
- **sqlalchemy**: Database ORM
- **schedule**: Task scheduling
- **pyyaml**: Config parsing
- **feedparser**: RSS parsing

### Performance
- Memory: ~50-100 MB
- CPU: Minimal (< 5% tijdens scraping)
- Network: ~1-5 MB per scrape cycle
- Disk: ~10 MB (database + logs)
