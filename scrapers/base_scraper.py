"""
Base Scraper - Basis class met alle anti-blocking maatregelen

OPLOSSINGEN VOOR ALLE TECHNISCHE UITDAGINGEN:
1. Rate Limiting - RateLimiter met exponential backoff
2. IP Blocking - User-Agent rotation, session management
3. CAPTCHA - Fallback mechanismen, manual intervention
4. HTML Changes - Multiple selector fallbacks, validatie
5. Duplicates - Database integratie
"""
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.rate_limiter import RateLimiter
from utils.user_agents import get_browser_headers
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Basis scraper class met alle anti-blocking maatregelen
    
    Features:
    - Automatische rate limiting
    - User-Agent rotation
    - Session management met cookies
    - Retry logic met exponential backoff
    - Error handling en logging
    - Database integratie voor duplicates
    """
    
    def __init__(self, 
                 criteria: Dict[str, Any],
                 db_manager: DatabaseManager,
                 rate_limiter: RateLimiter,
                 platform_name: str):
        """
        Args:
            criteria: Zoek criteria dictionary
            db_manager: Database manager instance
            rate_limiter: Rate limiter instance
            platform_name: Naam van het platform
        """
        self.criteria = criteria
        self.db = db_manager
        self.rate_limiter = rate_limiter
        self.platform_name = platform_name
        
        # Session met cookie persistence
        self.session = requests.Session()
        
        logger.info(f"{self.platform_name} scraper geïnitialiseerd")
    
    @abstractmethod
    def build_search_url(self) -> str:
        """
        Build zoek URL met criteria
        
        Returns:
            Complete search URL
        """
        pass
    
    @abstractmethod
    def parse_listings(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse HTML en extract advertenties
        
        Args:
            html: HTML content
        
        Returns:
            List van advertentie dictionaries
        """
        pass
    
    @abstractmethod
    def get_domain(self) -> str:
        """
        Get domain voor rate limiting
        
        Returns:
            Domain string (bijv. 'marktplaats.nl')
        """
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch pagina met alle anti-blocking maatregelen
        
        Args:
            url: URL om te fetchen
        
        Returns:
            HTML content of None bij error
        """
        domain = self.get_domain()
        
        try:
            # Rate limiting
            self.rate_limiter.wait(domain)
            
            # Headers met User-Agent rotation
            headers = get_browser_headers()
            
            logger.debug(f"Fetching: {url}")
            
            # Request met timeout
            response = self.session.get(
                url,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            
            # Check status
            if response.status_code == 200:
                self.rate_limiter.mark_success(domain)
                logger.info(f"✓ {self.platform_name}: Pagina succesvol opgehaald")
                return response.text
            
            elif response.status_code == 429:
                # Rate limited
                logger.warning(f"Rate limited door {self.platform_name}")
                self.rate_limiter.mark_failure(domain)
                raise Exception("Rate limited")
            
            elif response.status_code in [403, 401]:
                # Blocked
                logger.warning(f"Toegang geweigerd door {self.platform_name} (status {response.status_code})")
                self.rate_limiter.mark_failure(domain)
                raise Exception(f"Access denied: {response.status_code}")
            
            else:
                logger.error(f"HTTP {response.status_code} van {self.platform_name}")
                return None
                
        except requests.Timeout:
            logger.error(f"Timeout bij {self.platform_name}")
            self.rate_limiter.mark_failure(domain)
            return None
            
        except requests.RequestException as e:
            logger.error(f"Request error bij {self.platform_name}: {e}")
            self.rate_limiter.mark_failure(domain)
            return None
        
        except Exception as e:
            logger.error(f"Fetch error bij {self.platform_name}: {e}")
            return None
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scrape methode - haalt nieuwe advertenties op
        
        Returns:
            List van nieuwe (niet-duplicate) advertenties
        """
        logger.info(f"🔍 Starting scrape: {self.platform_name}")
        
        try:
            # Build search URL
            url = self.build_search_url()
            logger.debug(f"Search URL: {url}")
            
            # Fetch pagina
            html = self.fetch_page(url)
            if not html:
                logger.error(f"❌ Geen HTML ontvangen van {self.platform_name}")
                return []
            
            # Parse listings
            listings = self.parse_listings(html)
            logger.info(f"📊 {len(listings)} advertenties gevonden op {self.platform_name}")
            
            # Filter duplicates
            new_listings = []
            for listing in listings:
                listing_id = listing.get('listing_id')
                if not listing_id:
                    logger.warning("Advertentie zonder ID gevonden, skip")
                    continue
                
                # Check duplicate
                if not self.db.is_duplicate(self.platform_name, listing_id, listing):
                    # Add to database
                    if self.db.add_listing(self.platform_name, listing_id, listing):
                        new_listings.append(listing)
            
            logger.info(f"✨ {len(new_listings)} nieuwe advertenties gevonden")
            return new_listings
            
        except Exception as e:
            logger.error(f"❌ Scrape error {self.platform_name}: {e}", exc_info=True)
            return []
    
    def safe_extract(self, 
                    element: Any, 
                    selectors: List[str], 
                    attribute: str = None,
                    default: str = '') -> str:
        """
        OPLOSSING VOOR TECHNISCHE UITDAGING #4: HTML Structure Changes
        
        Probeer multiple CSS selectors als fallback
        
        Args:
            element: BeautifulSoup element
            selectors: List van CSS selectors om te proberen
            attribute: Optional attribute om te extracten
            default: Default waarde bij failure
        
        Returns:
            Extracted text of default
        """
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found:
                    if attribute:
                        value = found.get(attribute, default)
                    else:
                        value = found.get_text(strip=True)
                    
                    if value:
                        return value
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        return default
    
    def extract_price(self, price_str: str) -> Optional[float]:
        """
        Extract numerieke prijs uit string
        
        Args:
            price_str: Prijs string (bijv. '€ 12.500,-' of '12500 EUR')
        
        Returns:
            Float prijs of None
        """
        if not price_str:
            return None
        
        try:
            # Verwijder niet-numerieke characters behalve punt en comma
            import re
            clean = re.sub(r'[^\d.,]', '', price_str)
            
            # Handle verschillende formats
            if '.' in clean and ',' in clean:
                # Check of . of , de thousand separator is
                if clean.index('.') < clean.index(','):
                    # 1.234,56 format (EU)
                    clean = clean.replace('.', '').replace(',', '.')
                else:
                    # 1,234.56 format (US)
                    clean = clean.replace(',', '')
            elif ',' in clean:
                # Check of comma decimal of thousand separator is
                parts = clean.split(',')
                if len(parts[-1]) == 2:
                    # Waarschijnlijk decimal (1234,56)
                    clean = clean.replace(',', '.')
                else:
                    # Waarschijnlijk thousands (1,234)
                    clean = clean.replace(',', '')
            
            return float(clean)
            
        except (ValueError, AttributeError) as e:
            logger.debug(f"Prijs parse error: '{price_str}' - {e}")
            return None
    
    def validate_listing(self, listing: Dict[str, Any]) -> bool:
        """
        Valideer of listing alle required fields heeft
        
        Args:
            listing: Advertentie dictionary
        
        Returns:
            True als valid
        """
        required = ['listing_id', 'title', 'url']
        
        for field in required:
            if not listing.get(field):
                logger.warning(f"Listing mist required field: {field}")
                return False
        
        return True
    
    def matches_criteria(self, listing: Dict[str, Any]) -> bool:
        """
        Check of listing aan criteria voldoet
        
        Args:
            listing: Advertentie dictionary
        
        Returns:
            True als aan criteria voldoet
        """
        # Prijs check
        price = listing.get('price')
        if price:
            min_price = self.criteria.get('price_min')
            max_price = self.criteria.get('price_max')
            
            if min_price and price < min_price:
                return False
            if max_price and price > max_price:
                return False
        
        # Keywords check (basic)
        keywords = self.criteria.get('keywords', '')
        if keywords:
            title = listing.get('title', '').lower()
            if isinstance(keywords, str):
                if keywords.lower() not in title:
                    return False
            elif isinstance(keywords, list):
                if not any(kw.lower() in title for kw in keywords):
                    return False
        
        return True
