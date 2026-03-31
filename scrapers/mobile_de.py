"""
Mobile.de Scraper

Techniek: Web scraping
Moeilijkheid: Medium
Betrouwbaarheid: Goed
"""
import logging
from typing import Dict, List, Any
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class MobileDeScraper(BaseScraper):
    """
    Mobile.de scraper (Duitse auto platform)
    
    URL structuur:
    https://www.mobile.de/auto/search.html?{params}
    """
    
    BASE_URL = "https://www.mobile.de"
    
    def get_domain(self) -> str:
        return "mobile.de"
    
    def build_search_url(self) -> str:
        """Build Mobile.de zoek URL met criteria"""
        
        params = {}
        
        # Merk (make code - zou dynamisch moeten zijn)
        make = self.criteria.get('make', '').upper()
        if make:
            params['makeModelVariant1.makeId'] = make
        
        # Model
        model = self.criteria.get('model', '')
        if model:
            params['makeModelVariant1.modelDescription'] = model
        
        # Prijs
        if 'price_min' in self.criteria:
            params['minPrice'] = int(self.criteria['price_min'])
        if 'price_max' in self.criteria:
            params['maxPrice'] = int(self.criteria['price_max'])
        
        # Jaar
        if 'year_min' in self.criteria:
            params['minFirstRegistrationDate'] = self.criteria['year_min']
        if 'year_max' in self.criteria:
            params['maxFirstRegistrationDate'] = self.criteria['year_max']
        
        # Kilometerstand
        if 'mileage_max' in self.criteria:
            params['maxMileage'] = int(self.criteria['mileage_max'])
        
        # Postcode en radius
        if 'zip_code' in self.criteria:
            params['zipCode'] = self.criteria['zip_code']
        if 'radius_km' in self.criteria:
            params['scopeId'] = self.criteria['radius_km']
        
        # Sorteer op nieuwste
        params['sortOption.sortBy'] = 'creationTime'
        params['sortOption.sortOrder'] = 'DESCENDING'
        
        # Build URL
        base = f"{self.BASE_URL}/auto/search.html"
        if params:
            url = f"{base}?{urlencode(params)}"
        else:
            url = base
        
        return url
    
    def parse_listings(self, html: str) -> List[Dict[str, Any]]:
        """Parse Mobile.de HTML voor advertenties"""
        
        soup = BeautifulSoup(html, 'lxml')
        listings = []
        
        # Mobile.de gebruikt div.cBox-body voor listings
        listing_items = soup.select('div.cBox-body--resultitem, article.vehicle-data, div[data-ad-id]')
        
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
            item.get('data-ad-id') or
            item.get('data-id') or
            self.safe_extract(item, ['[data-ad-id]'], 'data-ad-id')
        )
        
        # Title
        title = self.safe_extract(
            item,
            [
                'h2.vehicle-data--title',
                'h3.headline-block',
                '.g-col-12 h2',
                '[data-testid="result-title"]'
            ]
        )
        
        # URL
        url_element = item.select_one('a.link--inherit, a[href*="/auto-inserat/"]')
        url = ''
        if url_element:
            url = url_element.get('href', '')
            if url and not url.startswith('http'):
                url = self.BASE_URL + url
        
        # Prijs
        price_text = self.safe_extract(
            item,
            [
                'span.price-block__price',
                'span.h3.u-text-orange',
                '[data-testid="prime-price"]',
                '.price'
            ]
        )
        price = self.extract_price(price_text)
        
        # Afbeelding
        image_url = self.safe_extract(
            item,
            [
                'img.img-responsive',
                'img[data-src]',
                'picture img'
            ],
            attribute='src'
        )
        if not image_url:
            image_url = self.safe_extract(
                item,
                ['img[data-src]', 'img[data-lazy]'],
                attribute='data-src'
            )
        
        # Locatie
        location = self.safe_extract(
            item,
            [
                '.vehicle-data--location',
                '[data-testid="result-location"]',
                '.seller-info'
            ]
        )
        
        # Details
        details = self.safe_extract(
            item,
            [
                '.vehicle-data--details',
                '.u-margin-bottom-9',
                '[data-testid="result-details"]'
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
