"""
Facebook Marketplace Scraper - VPS versie
Draait elke minuut via cron, gebruikt Playwright met een opgeslagen sessie.
Schrijft naar dezelfde Supabase database als de Vercel bot.

Proxy instelling (optioneel): zet PROXY_SERVER in .env om datacenter-IP blokkade te omzeilen.
Bijvoorbeeld: PROXY_SERVER=socks5://user:pass@host:port
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from supabase import create_client

load_dotenv()

PROXY_SERVER = os.environ.get("PROXY_SERVER")  # optioneel, bv. socks5://user:pass@host:port

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SESSION_FILE = Path(__file__).parent / "fb_session.json"


async def save_session(context):
    """Sla de huidige browser sessie op zodat we niet opnieuw hoeven in te loggen."""
    storage = await context.storage_state()
    SESSION_FILE.write_text(json.dumps(storage))
    print("[sessie] Opgeslagen.")


async def login_facebook(page):
    """Log in op Facebook. Alleen nodig als er nog geen sessie is."""
    print("[login] Inloggen op Facebook...")
    await page.goto("https://www.facebook.com/login", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)

    # Accepteer cookies als dat popup verschijnt
    try:
        await page.click('[data-testid="cookie-policy-manage-dialog-accept-button"]', timeout=5000)
    except PlaywrightTimeout:
        pass
    try:
        await page.get_by_role("button", name=re.compile(r"(Accept|Accepteer|Alles accepteren)", re.IGNORECASE)).click(timeout=5000)
    except PlaywrightTimeout:
        pass

    fb_email = os.environ.get("FACEBOOK_EMAIL")
    fb_password = os.environ.get("FACEBOOK_PASSWORD")

    if not fb_email or not fb_password:
        print("[ERROR] FACEBOOK_EMAIL en FACEBOOK_PASSWORD zijn niet ingesteld in .env")
        sys.exit(1)

    await page.fill("#email", fb_email)
    await page.fill("#pass", fb_password)
    await page.click("#loginbutton")
    await page.wait_for_timeout(4000)

    if "login" in page.url or "checkpoint" in page.url:
        print("[ERROR] Login mislukt of 2FA vereist. Open de browser handmatig:")
        print("  python scraper.py --login")
        sys.exit(1)

    print("[login] Succesvol ingelogd!")


async def get_facebook_config():
    """Haal de Facebook platform config op uit Supabase."""
    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    result = sb.table("platforms").select("*").eq("id", "facebook").eq("enabled", True).execute()
    if not result.data:
        return None
    return result.data[0].get("config") or {}


async def listing_already_known(listing_id: str) -> bool:
    """Check of de listing al in Supabase staat."""
    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    result = sb.table("listings").select("id").eq("listing_id", listing_id).execute()
    return bool(result.data)


async def save_listing(listing: dict):
    """Sla een nieuwe listing op in Supabase."""
    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    sb.table("listings").insert({
        "listing_id": listing["listing_id"],
        "platform": "facebook",
        "title": listing.get("title", ""),
        "price": listing.get("price"),
        "year": listing.get("year"),
        "mileage": listing.get("mileage"),
        "url": listing.get("url", ""),
        "location": listing.get("location", ""),
        "image_url": listing.get("image_url", ""),
        "created_at": datetime.now().isoformat(),
    }).execute()


async def send_telegram(listing: dict):
    """Stuur een Telegram notificatie."""
    import httpx
    price_str = f"€{listing['price']:,.0f}" if listing.get("price") else "Prijs onbekend"
    location_str = f"📍 {listing['location']}" if listing.get("location") else ""

    text = (
        f"🚗 <b>Nieuwe advertentie gevonden!</b>\n\n"
        f"<b>{listing['title']}</b>\n"
        f"💶 {price_str}\n"
        f"{location_str}\n\n"
        f"🔗 <a href='{listing['url']}'>Bekijk advertentie</a>"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
        )


def passes_filter(listing: dict, config: dict) -> bool:
    """Controleer of een listing voldoet aan de criteria."""
    price = listing.get("price") or 0

    if config.get("price_max"):
        if price == 0 or price > float(config["price_max"]):
            return False
    if config.get("price_min"):
        if price == 0 or price < float(config["price_min"]):
            return False

    return True


async def scrape(page, config: dict) -> list:
    """Scrape Facebook Marketplace listings."""
    keywords = config.get("keywords", "auto")
    location = config.get("location", "nederland")
    price_max = config.get("price_max")
    price_min = config.get("price_min")

    # Bouw de zoek-URL
    url = f"https://www.facebook.com/marketplace/{location.lower().replace(' ', '')}/search?query={keywords.replace(' ', '%20')}&exact=false"
    if price_max:
        url += f"&maxPrice={int(price_max)}"
    if price_min:
        url += f"&minPrice={int(price_min)}"

    print(f"[scrape] Ophalen: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(3000)

    # Scroll een paar keer om meer listings te laden
    for _ in range(3):
        await page.evaluate("window.scrollBy(0, 1000)")
        await page.wait_for_timeout(1000)

    # Extraheer listings via JavaScript uit de pagina
    listings_data = await page.evaluate("""
        () => {
            const results = [];
            const cards = document.querySelectorAll('div[data-testid="marketplace_feed_item"], a[href*="/marketplace/item/"]');
            const seen = new Set();

            document.querySelectorAll('a[href*="/marketplace/item/"]').forEach(a => {
                const href = a.href || '';
                const match = href.match(/\\/marketplace\\/item\\/(\\d+)/);
                if (!match) return;
                const id = match[1];
                if (seen.has(id)) return;
                seen.add(id);

                // Prijs
                const allText = a.innerText || '';
                const priceMatch = allText.match(/€\\s?([\\d\\.]+)/);
                const price = priceMatch ? parseFloat(priceMatch[1].replace('.', '')) : 0;

                // Titel - eerste grote tekst
                const spans = a.querySelectorAll('span');
                let title = '';
                for (const span of spans) {
                    const t = span.innerText?.trim();
                    if (t && t.length > 5 && !t.startsWith('€')) {
                        title = t;
                        break;
                    }
                }

                // Locatie - tweede stuk tekst
                let location = '';
                const lines = allText.split('\\n').map(l => l.trim()).filter(Boolean);
                if (lines.length >= 3) location = lines[lines.length - 1];

                // Afbeelding
                const img = a.querySelector('img');
                const imageUrl = img ? img.src : '';

                results.push({
                    id,
                    title,
                    price,
                    location,
                    image_url: imageUrl,
                    url: `https://www.facebook.com/marketplace/item/${id}/`
                });
            });

            return results;
        }
    """)

    listings = []
    for item in listings_data:
        listing_id = f"fb_{item['id']}"
        listings.append({
            "listing_id": listing_id,
            "platform": "facebook",
            "title": item.get("title", ""),
            "price": float(item.get("price") or 0),
            "year": None,
            "mileage": None,
            "url": item.get("url", ""),
            "location": item.get("location", ""),
            "image_url": item.get("image_url", ""),
        })

    print(f"[scrape] {len(listings)} listings gevonden")
    return listings


async def run_scraper():
    """Hoofdfunctie: scrape en verwerk nieuwe listings."""
    config = await get_facebook_config()
    if config is None:
        print("[info] Facebook platform is uitgeschakeld of niet geconfigureerd. Stop.")
        return

    async with async_playwright() as p:
        # Gebruik opgeslagen sessie als die bestaat
        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ]
        proxy_config = {"server": PROXY_SERVER} if PROXY_SERVER else None
        if PROXY_SERVER:
            print(f"[proxy] Gebruikt proxy: {PROXY_SERVER.split('@')[-1]}")

        browser = await p.chromium.launch(
            headless=True,
            args=launch_args,
            proxy=proxy_config,
        )

        context_kwargs = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "viewport": {"width": 1280, "height": 800},
            "locale": "nl-NL",
            "timezone_id": "Europe/Amsterdam",
        }

        if SESSION_FILE.exists():
            print("[sessie] Opgeslagen sessie laden...")
            storage_state = json.loads(SESSION_FILE.read_text())
            context = await browser.new_context(
                storage_state=storage_state,
                **context_kwargs,
            )
        else:
            context = await browser.new_context(**context_kwargs)

        page = await context.new_page()

        # Check of sessie nog geldig is
        await page.goto("https://www.facebook.com/marketplace/", wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(2000)

        if "login" in page.url:
            print("[sessie] Sessie verlopen, opnieuw inloggen...")
            await login_facebook(page)
            await save_session(context)

        # Scrape listings
        listings = await scrape(page, config)

        # Sla sessie altijd op na succesvolle scrape (houdt cookies vers)
        await save_session(context)
        await browser.close()

    # Verwerk nieuwe listings
    new_count = 0
    for listing in listings:
        if not passes_filter(listing, config):
            continue
        if await listing_already_known(listing["listing_id"]):
            continue

        await save_listing(listing)
        await send_telegram(listing)
        new_count += 1
        print(f"[nieuw] {listing['title']} — €{listing['price']:,.0f}")

    print(f"[klaar] {len(listings)} gescraped, {new_count} nieuw, {datetime.now().strftime('%H:%M:%S')}")


async def interactive_login():
    """Eenmalige handmatige login met zichtbare browser (voor 2FA etc.)"""
    print("[login] Browser openen voor handmatige login...")
    proxy_config = {"server": PROXY_SERVER} if PROXY_SERVER else None
    if PROXY_SERVER:
        print(f"[proxy] Gebruikt proxy: {PROXY_SERVER.split('@')[-1]}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, proxy=proxy_config)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="nl-NL",
            timezone_id="Europe/Amsterdam",
        )
        page = await context.new_page()
        await page.goto("https://www.facebook.com/login")
        print("[login] Log in op Facebook in de browser die net is geopend.")
        print("[login] Druk daarna op ENTER hier om de sessie op te slaan...")
        input()
        await save_session(context)
        await browser.close()
    print("[login] Sessie opgeslagen! Je kan nu 'python scraper.py' draaien.")


if __name__ == "__main__":
    if "--login" in sys.argv:
        asyncio.run(interactive_login())
    else:
        asyncio.run(run_scraper())
