# 🚀 SNELLE START GUIDE

## Stap 1: Telegram Bot Aanmaken (2 minuten)

### A. Maak een bot aan
1. Open Telegram app
2. Zoek naar: **@BotFather**
3. Start chat en stuur: `/newbot`
4. Volg instructies:
   - Geef bot een naam (bijv: "Mijn Auto Bot")
   - Geef bot een username (bijv: "mijnauto_notify_bot")
5. **Kopieer de Bot Token** die je krijgt (bijv: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### B. Krijg je Chat ID
1. Start chat met je nieuwe bot (click op link in BotFather bericht)
2. **BELANGRIJK**: Stuur `/start` of een willekeurig bericht naar je bot (bijv: "hallo")
   - Dit is essentieel! Anders krijg je 404 error.
3. **NA het sturen** van bericht, open in browser: 
   ```
   https://api.telegram.org/bot<JE_BOT_TOKEN>/getUpdates
   ```
   - Vervang `<JE_BOT_TOKEN>` met je token uit stap A5
   - Bijvoorbeeld: `https://api.telegram.org/bot123456:ABC-DEF/getUpdates`
4. Je ziet JSON response met tekst, zoek naar `"chat":{"id":123456789`
5. **Kopieer dit getal** (bijv: `123456789`)

**Krijg je nog steeds 404 of empty result?**
- Zorg dat je **eerst een bericht hebt gestuurd** naar de bot in Telegram
- Wacht 5 seconden en refresh de browser
- Alternatief: gebruik [@userinfobot](https://t.me/userinfobot) - stuur `/start` en je krijgt je Chat ID direct!

## Stap 2: Vul .env File In

Open `.env` file en vervang:
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

## Stap 3: Test De Bot

```powershell
python main.py --test
```

Je moet nu een test bericht ontvangen in Telegram! ✅

## Stap 4: Configureer Zoek Criteria

Edit `config.yaml`:
```yaml
platforms:
  marktplaats:
    enabled: true
    criteria:
      keywords: "bmw 320d"  # ← Jouw zoekopdracht
      price_min: 5000       # ← Min prijs
      price_max: 15000      # ← Max prijs
```

## Stap 5: Run De Bot

```powershell
# Test eenmalig
python main.py --once

# Start bot (blijft draaien)
python main.py
```

## 🆘 Hulp Nodig?

### Error: "No module named 'yaml'"
```powershell
pip install -r requirements.txt
```

### Error: "Telegram credentials niet geconfigureerd"
- Check `.env` file
- Zorg dat BOT_TOKEN en CHAT_ID correct zijn ingevuld

### Geen test bericht ontvangen?
1. Check of bot token correct is
2. Check of je chat ID correct is
3. Stuur eerst bericht naar bot voordat je chat ID ophaalt
4. Check logs: `logs/bot.log`

## 📚 Meer Info

- Uitgebreide handleiding: `DOCUMENTATION.md`
- Technische details: `TECHNICAL_EXPLANATION.md`
- Project overzicht: `README.md`
