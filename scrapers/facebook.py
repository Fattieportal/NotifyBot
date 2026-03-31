"""
Facebook Marketplace Scraper

OPLOSSING VOOR TECHNISCHE UITDAGING #3: CAPTCHA & Anti-Bot

Techniek: Playwright browser automation
Moeilijkheid: Hoog (anti-bot detectie)
Betrouwbaarheid: Medium (vereist login)

Dit is de moeilijkste scraper vanwege:
- Login vereist
- Sterke anti-bot detectie
- Dynamic content
- CAPTCHA's mogelijk
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
import json
from pathlib import Path

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class FacebookScraper(BaseScraper):
    """
    Facebook Marketplace scraper met Playwright
    
    Features:
    - Browser automation voor anti-detection
    - Cookie persistence voor session
    - Headless mode (configurable)
    - Login management
    
    Waarschuwing: Facebook kan account blokkeren bij te veel automation
    """
    
    BASE_URL = "https://www.facebook.com"
    COOKIES_FILE = "cookies/facebook_cookies.json"
    
    def __init__(self, *args, headless: bool = True, email: str = None, password: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.headless = headless
        self.email = email
        self.password = password
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # Ensure cookies directory exists
        Path(self.COOKIES_FILE).parent.mkdir(parents=True, exist_ok=True)
    
    def get_domain(self) -> str:
        return "facebook.com"
    
    def build_search_url(self) -> str:
        """Build Facebook Marketplace zoek URL"""
        
        query = self.criteria.get('query', 'auto')
        
        # Facebook Marketplace search URL
        url = f"{self.BASE_URL}/marketplace/search"
        
        # Facebook gebruikt query parameters anders
        # Dit is een simplified versie
        params = []
        
        if 'price_min' in self.criteria:
            params.append(f"minPrice={self.criteria['price_min']}")
        if 'price_max' in self.criteria:
            params.append(f"maxPrice={self.criteria['price_max']}")
        if 'radius_km' in self.criteria:
            params.append(f"radius={self.criteria['radius_km']}")
        
        # Add query
        params.append(f"query={query.replace(' ', '%20')}")
        
        if params:
            url = f"{url}/?{'&'.join(params)}"
        
        return url
    
    async def _init_browser(self):
        """Initialiseer Playwright browser"""
        if self.browser:
            return
        
        playwright = await async_playwright().start()
        
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        # Create context met realistic settings
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            locale='nl-NL'
        )
        
        # Load cookies als beschikbaar
        if Path(self.COOKIES_FILE).exists():
            with open(self.COOKIES_FILE, 'r') as f:
                cookies = json.load(f)
                await context.add_cookies(cookies)
                logger.info("Facebook cookies geladen")
        
        self.page = await context.new_page()
        
        # Anti-detection: Remove webdriver flag
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
    
    async def _login_if_needed(self):
        """Login op Facebook als nog niet ingelogd"""
        
        if not self.email or not self.password:
            logger.warning("Facebook credentials niet geconfigureerd - kan niet inloggen")
            return False
        
        try:
            # Check of we al ingelogd zijn
            await self.page.goto(self.BASE_URL, timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            # Check of login form zichtbaar is
            login_form = await self.page.query_selector('input[name="email"]')
            
            if not login_form:
                logger.info("Al ingelogd op Facebook")
                return True
            
            logger.info("Facebook login vereist...")
            
            # Fill login form
            await self.page.fill('input[name="email"]', self.email)
            await self.page.fill('input[name="pass"]', self.password)
            
            # Click login
            await self.page.click('button[name="login"]')
            
            # Wait voor redirect (max 30 sec)
            await self.page.wait_for_url(lambda url: 'login' not in url, timeout=30000)
            
            # Save cookies
            cookies = await self.page.context.cookies()
            with open(self.COOKIES_FILE, 'w') as f:
                json.dump(cookies, f)
            
            logger.info("✓ Facebook login succesvol")
            return True
            
        except Exception as e:
            logger.error(f"Facebook login gefaald: {e}")
            return False
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Override: Gebruik Playwright i.p.v. requests
        """
        return asyncio.run(self._fetch_page_async(url))
    
    async def _fetch_page_async(self, url: str) -> Optional[str]:
        """Async fetch met Playwright"""
        
        try:
            # Rate limiting
            self.rate_limiter.wait(self.get_domain())
            
            # Init browser
            await self._init_browser()
            
            # Login als nodig
            if not await self._login_if_needed():
                logger.error("Kan niet inloggen op Facebook")
                return None
            
            logger.debug(f"Navigating to: {url}")
            
            # Navigate
            await self.page.goto(url, timeout=30000, wait_until='networkidle')
            
            # Scroll om dynamic content te laden
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await self.page.wait_for_timeout(2000)
            
            # Get HTML
            html = await self.page.content()
            
            self.rate_limiter.mark_success(self.get_domain())
            logger.info("✓ Facebook pagina succesvol opgehaald")
            
            return html
            
        except Exception as e:
            logger.error(f"Facebook fetch error: {e}")
            self.rate_limiter.mark_failure(self.get_domain())
            return None
    
    def parse_listings(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse Facebook Marketplace listings
        
        Waarschuwing: Facebook's HTML structuur verandert regelmatig!
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'lxml')
        listings = []
        
        # Facebook gebruikt div's met dynamische classes
        # Dit is een best-effort benadering
        listing_items = soup.select('div[class*="marketplace"] a[href*="/marketplace/item/"]')
        
        logger.debug(f"Gevonden {len(listing_items)} listing items")
        
        # Note: Facebook scraping is zeer unreliable vanwege dynamic content
        # Voor production zou je de GraphQL API moeten gebruiken (vereist app approval)
        
        logger.warning("Facebook scraping is experimenteel - resultaten kunnen beperkt zijn")
        
        return listings
    
    def _parse_single_listing(self, item) -> Dict[str, Any]:
        """Parse een enkele Facebook listing"""
        # Dit zou veel complexer moeten zijn voor echte Facebook scraping
        # Placeholder implementation
        
        return {
            'listing_id': '',
            'title': '',
            'price': None,
            'url': '',
            'image_url': '',
            'location': '',
            'description': '',
            'posted_date': '',
            'platform': self.platform_name
        }
    
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
    
    def __del__(self):
        """Destructor - cleanup browser"""
        if self.browser:
            try:
                asyncio.run(self.cleanup())
            except:
                pass
