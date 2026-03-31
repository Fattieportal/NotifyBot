"""
AutoScout24 Scraper

Techniek: Web scraping + mogelijke API calls
Moeilijkheid: Medium
Betrouwbaarheid: Goed
"""
import logging
from typing import Dict, List, Any
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class AutoScoutScraper(BaseScraper):
    """
    AutoScout24 scraper (.nl, .de, .be supported)
    
    URL structuur:
    https://www.autoscout24.nl/lst/{make}/{model}
    """
    
    BASE_URL = "https://www.autoscout24.nl"
    
    # Brandstof type mapping
    FUEL_TYPES = {
        'Diesel': 'D',
        'Petrol': 'B',
        'Electric': 'E',
        'Hybrid': 'H'
    }
    
    def get_domain(self) -> str:
        return "autoscout24.nl"
    
    def build_search_url(self) -> str:
        """Build AutoScout zoek URL met criteria"""
        
        # Query parameters
        params = {}
        
        # Merk en model
        make = self.criteria.get('make', '').lower().replace(' ', '-')
        model = self.criteria.get('model', '').lower().replace(' ', '-')
        
        if make and model:
            base = f"{self.BASE_URL}/lst/{make}/{model}"
        elif make:
            base = f"{self.BASE_URL}/lst/{make}"
        else:
            base = f"{self.BASE_URL}/lst"
        
        # Prijs
        if 'price_min' in self.criteria:
            params['pricefrom'] = int(self.criteria['price_min'])
        if 'price_max' in self.criteria:
            params['priceto'] = int(self.criteria['price_max'])
        
        # Jaar
        if 'year_min' in self.criteria:
            params['fregfrom'] = self.criteria['year_min']
        if 'year_max' in self.criteria:
            params['fregto'] = self.criteria['year_max']
        
        # Kilometerstand
        if 'mileage_max' in self.criteria:
            params['kmto'] = int(self.criteria['mileage_max'])
        
        # Brandstof type
        fuel = self.criteria.get('fuel_type')
        if fuel in self.FUEL_TYPES:
            params['fuel'] = self.FUEL_TYPES[fuel]
        
        # Sorteer op nieuwste
        params['sort'] = 'age'
        params['desc'] = '1'
        
        # Build URL
        if params:
            url = f"{base}?{urlencode(params)}"
        else:
            url = base
        
        return url
    
    def parse_listings(self, html: str) -> List[Dict[str, Any]]:
        """Parse AutoScout HTML voor advertenties"""
        
        soup = BeautifulSoup(html, 'lxml')
        listings = []
        
        # AutoScout gebruikt article tags voor listings
        listing_items = soup.select('article[data-item-id], article.cldt-summary-full-item, div[data-listing-id]')
        
        logger.debug(f"Gevonden {len(listing_items)} listing items")
        
        for item in listing_items:
            try:
                listing = self._parse_single_listing(item)
                if listing and self.validate_listing(listing):
                    if self.matches_criteria(listing):
                        listings.append(listing)
            except Exception as e:
                logger.debug(f"Error parsing listing item: {e}")
                continue
        
        return listings
    
    def _parse_single_listing(self, item) -> Dict[str, Any]:
        """Parse een enkele advertentie"""
        
        # Listing ID
        listing_id = (
            item.get('data-item-id') or
            item.get('data-listing-id') or
            item.get('id', '').split('-')[-1]
        )
        
        # Title
        title = self.safe_extract(
            item,
            [
                'h2[data-item-name]',
                'h2.cldt-summary-titles',
                '.cldt-summary-makemodel',
                '[class*="ListItem_title"]'
            ]
        )
        
        # URL
        url_element = item.select_one('a[href*="/lst/"]')
        url = ''
        if url_element:
            url = url_element.get('href', '')
            if url and not url.startswith('http'):
                url = self.BASE_URL + url
        
        # Prijs
        price_text = self.safe_extract(
            item,
            [
                'span[data-item-price]',
                '.cldt-price',
                '[class*="Price_price"]',
                '[class*="price"]'
            ]
        )
        price = self.extract_price(price_text)
        
        # Afbeelding
        image_url = self.safe_extract(
            item,
            [
                'img.cldt-summary-image',
                'img[data-src]',
                'picture img'
            ],
            attribute='src'
        )
        if not image_url:
            image_url = self.safe_extract(
                item,
                ['img[data-src]'],
                attribute='data-src'
            )
        
        # Locatie
        location = self.safe_extract(
            item,
            [
                '.cldt-summary-seller-contact-zip-city',
                '[class*="location"]',
                '.seller-info'
            ]
        )
        
        # Kilometerstand & jaar uit summary
        details = self.safe_extract(
            item,
            [
                '.cldt-summary-details',
                '.vehicle-data',
                '[class*="VehicleDetailTable"]'
            ]
        )
        
        return {
            'listing_id': listing_id,
            'title': title,
            'price': price,
            'url': url,
            'image_url': image_url,
            'location': location,
            'description': details,
            'posted_date': 'Recent',
            'platform': self.platform_name
        }
