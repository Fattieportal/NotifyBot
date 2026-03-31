"""
eBay Kleinanzeigen Scraper

Techniek: RSS Feeds (meest betrouwbaar!)
Moeilijkheid: Laag
Betrouwbaarheid: Excellent

eBay Kleinanzeigen heeft RSS feeds voor zoekopdrachten!
Dit is de meest betrouwbare methode.
"""
import logging
from typing import Dict, List, Any
from urllib.parse import urlencode
import feedparser

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class EbayKleinanzeigenScraper(BaseScraper):
    """
    eBay Kleinanzeigen scraper via RSS feeds
    
    RSS feed URL:
    https://www.kleinanzeigen.de/s-autos/anzeige:angebote/seite:1/{query}/k0c216?format=rss
    
    Voordeel: RSS is officieel supported en zeer stabiel!
    """
    
    BASE_URL = "https://www.kleinanzeigen.de"
    
    def get_domain(self) -> str:
        return "kleinanzeigen.de"
    
    def build_search_url(self) -> str:
        """Build eBay Kleinanzeigen RSS URL"""
        
        # Keywords
        keywords = self.criteria.get('keywords', 'auto')
        if isinstance(keywords, list):
            keywords = '+'.join(keywords)
        keywords = keywords.replace(' ', '+')
        
        # Category 216 = Auto's
        category = self.criteria.get('category', '216')
        
        # Basis RSS URL
        base = f"{self.BASE_URL}/s-autos/anzeige:angebote/{keywords}/k0c{category}"
        
        # Query parameters voor RSS
        params = {
            'format': 'rss'
        }
        
        # Prijs range (als URL parameters)
        price_min = self.criteria.get('price_min')
        price_max = self.criteria.get('price_max')
        
        if price_min or price_max:
            price_str = f"preis:{price_min or ''}:{price_max or ''}"
            base = f"{base}/{price_str}"
        
        # Postcode en radius
        zip_code = self.criteria.get('zip_code')
        radius = self.criteria.get('radius_km', 50)
        
        if zip_code:
            params['zipCode'] = zip_code
            params['radius'] = radius
        
        url = f"{base}?{urlencode(params)}"
        return url
    
    def fetch_page(self, url: str) -> str:
        """
        Override: Parse RSS feed i.p.v. HTML
        Returns RSS XML as string
        """
        domain = self.get_domain()
        
        try:
            # Rate limiting
            self.rate_limiter.wait(domain)
            
            logger.debug(f"Fetching RSS: {url}")
            
            # Parse RSS feed
            feed = feedparser.parse(url)
            
            if feed.bozo:
                # Feed parse error
                logger.error(f"RSS parse error: {feed.bozo_exception}")
                self.rate_limiter.mark_failure(domain)
                return ""
            
            self.rate_limiter.mark_success(domain)
            logger.info(f"✓ RSS feed opgehaald: {len(feed.entries)} entries")
            
            # Return as "HTML" (we'll parse in parse_listings)
            return str(feed)
            
        except Exception as e:
            logger.error(f"RSS fetch error: {e}")
            self.rate_limiter.mark_failure(domain)
            return ""
    
    def parse_listings(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse RSS feed entries
        
        Args:
            html: Actually contains RSS feed data (we re-fetch it here)
        """
        try:
            # Re-build URL en parse feed
            url = self.build_search_url()
            feed = feedparser.parse(url)
            
            listings = []
            
            for entry in feed.entries:
                try:
                    listing = self._parse_rss_entry(entry)
                    
                    if listing and self.validate_listing(listing):
                        if self.matches_criteria(listing):
                            listings.append(listing)
                        else:
                            logger.debug(f"Listing voldoet niet aan criteria: {listing.get('title')}")
                            
                except Exception as e:
                    logger.debug(f"Error parsing RSS entry: {e}")
                    continue
            
            return listings
            
        except Exception as e:
            logger.error(f"RSS parse error: {e}")
            return []
    
    def _parse_rss_entry(self, entry) -> Dict[str, Any]:
        """
        Parse een RSS feed entry
        
        Args:
            entry: feedparser entry object
        """
        # RSS entries hebben mooie gestructureerde data!
        
        # Listing ID uit URL
        url = entry.get('link', '')
        listing_id = url.split('/')[-1] if url else ''
        
        # Title
        title = entry.get('title', '')
        
        # Beschrijving
        description = entry.get('summary', '')
        
        # Prijs uit description of custom fields
        price = None
        price_str = entry.get('price', '')
        if price_str:
            price = self.extract_price(price_str)
        else:
            # Try to extract from description
            import re
            price_match = re.search(r'(\d+[\.,]\d+|\d+)\s*€', description)
            if price_match:
                price = self.extract_price(price_match.group(0))
        
        # Afbeelding uit enclosure
        image_url = ''
        if hasattr(entry, 'enclosures') and entry.enclosures:
            image_url = entry.enclosures[0].get('href', '')
        
        # Locatie uit beschrijving of custom fields
        location = entry.get('location', '')
        if not location:
            # Try to extract from description
            import re
            loc_match = re.search(r'\d{5}\s+[\w\s]+', description)
            if loc_match:
                location = loc_match.group(0)
        
        # Published date
        posted_date = entry.get('published', '')
        
        return {
            'listing_id': listing_id,
            'title': title,
            'price': price,
            'url': url,
            'image_url': image_url,
            'location': location,
            'description': description[:500],  # Truncate
            'posted_date': posted_date,
            'platform': self.platform_name
        }
