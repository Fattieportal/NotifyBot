# Facebook Marketplace Scraper — VPS Setup

## Stap 1: VPS aanmaken
1. Ga naar [hetzner.com](https://hetzner.com) → Cloud → New Project
2. Maak een server aan:
   - **Type**: CAX11 (€3.29/maand)
   - **OS**: Ubuntu 24.04
   - **Locatie**: Duitsland (dichtst bij NL)
3. Kopieer het IP-adres

## Stap 2: Inloggen op VPS
```bash
ssh root@JOUW-IP
```

## Stap 3: Python + Playwright installeren
```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git -y

cd /root
git clone https://github.com/Fattieportal/NotifyBot.git
cd NotifyBot/facebook-scraper

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
```

## Stap 4: .env instellen
```bash
cp .env.example .env
nano .env
```
Vul alle waarden in (zelfde als je Vercel env vars + je Facebook login).

## Stap 5: Eenmalig inloggen op Facebook
```bash
# Dit opent GEEN browser op de VPS (headless server).
# We gebruiken je lokale PC voor de eerste login.
# Op jouw LOKALE PC (niet VPS):
cd "c:\Users\Gslik\Notify bot\facebook-scraper"
pip install -r requirements.txt
playwright install chromium
python scraper.py --login
```
Er opent een browser → log in op Facebook → druk ENTER.
Dit maakt `fb_session.json` aan op je lokale PC.

Upload daarna het sessie-bestand naar de VPS:
```bash
# Op jouw lokale PC:
scp fb_session.json root@JOUW-IP:/root/NotifyBot/facebook-scraper/
```

## Stap 6: Test of het werkt
```bash
# Op de VPS:
cd /root/NotifyBot/facebook-scraper
source venv/bin/activate
python scraper.py
```
Je zou output moeten zien zoals:
```
[sessie] Opgeslagen sessie laden...
[scrape] 25 listings gevonden
[nieuw] BMW 320i 2015 — €12.500
[klaar] 25 gescraped, 1 nieuw, 14:32:01
```

## Stap 7: Cron instellen (elke minuut automatisch)
```bash
crontab -e
```
Voeg toe onderaan:
```
* * * * * /root/NotifyBot/facebook-scraper/venv/bin/python /root/NotifyBot/facebook-scraper/scraper.py >> /root/NotifyBot/facebook-scraper/scraper.log 2>&1
```

## Stap 8: Logs bekijken
```bash
tail -f /root/NotifyBot/facebook-scraper/scraper.log
```

## Sessie verversen
Als Facebook je uitlogt (gebeurt na weken/maanden):
```bash
# Op lokale PC opnieuw:
python scraper.py --login
scp fb_session.json root@JOUW-IP:/root/NotifyBot/facebook-scraper/
```

## Facebook platform aanzetten in Supabase
Zet in de `platforms` tabel:
- `id`: `facebook`
- `enabled`: `true`
- `config`:
```json
{
  "keywords": "bmw",
  "location": "amsterdam",
  "price_max": 15000,
  "price_min": 1000
}
```
