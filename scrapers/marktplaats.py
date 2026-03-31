"""
Marktplaats.nl Scraper

Techniek: Web scraping met BeautifulSoup
Moeilijkheid: Medium
Betrouwbaarheid: Goed
"""
import logging
from typing import Dict, List, Any
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class MarktplaatsScraper(BaseScraper):
    """
    Marktplaats.nl scraper
    
    URL structuur:
    https://www.marktplaats.nl/l/auto-s/#{query parameters}
    """
    
    BASE_URL = "https://www.marktplaats.nl"
    
    def get_domain(self) -> str:
        return "marktplaats.nl"
    
    def build_search_url(self) -> str:
        """Build Marktplaats zoek URL met criteria"""
        
        # Basis URL voor auto's
        base = f"{self.BASE_URL}/l/auto-s/"
        
        # Query parameters
        params = {}
        
        # Keywords
        if 'keywords' in self.criteria:
            keywords = self.criteria['keywords']
            if isinstance(keywords, list):
                keywords = ' '.join(keywords)
            params['query'] = keywords
        
        # Prijs range
        if 'price_min' in self.criteria:
            params['priceFrom'] = int(self.criteria['price_min'])
        if 'price_max' in self.criteria:
            params['priceTo'] = int(self.criteria['price_max'])
        
        # Jaar
        if 'year_min' in self.criteria:
            params['yearFrom'] = self.criteria['year_min']
        if 'year_max' in self.criteria:
            params['yearTo'] = self.criteria['year_max']
        
        # Kilometerstand
        if 'mileage_max' in self.criteria:
            params['mileageTo'] = int(self.criteria['mileage_max'])
        
        # Postcode en afstand
        if 'postcode' in self.criteria:
            params['postcode'] = self.criteria['postcode']
        if 'distance_km' in self.criteria:
            params['distanceMeters'] = self.criteria['distance_km'] * 1000
        
        # Sorteer op nieuwste eerst
        params['sortBy'] = 'SORT_INDEX'
        params['sortOrder'] = 'DECREASING'
        
        # Build URL
        if params:
            url = f"{base}?{urlencode(params)}"
        else:
            url = base
        
        return url
    
    def parse_listings(self, html: str) -> List[Dict[str, Any]]:
        """Parse Marktplaats HTML voor advertenties"""
        
        soup = BeautifulSoup(html, 'lxml')
        listings = []
        
        # Marktplaats gebruikt verschillende selectors - gebruik fallbacks
        # Selecteer alle advertentie items
        listing_items = soup.select('li.hz-Listing, article.hz-Listing, div[data-item-id]')
        
        logger.debug(f"Gevonden {len(listing_items)} listing items")
        
        for item in listing_items:
            try:
                listing = self._parse_single_listing(item)
                if listing and self.validate_listing(listing):
                    if self.matches_criteria(listing):
                        listings.append(listing)
                    else:
                        logger.debug(f"Listing voldoet niet aan criteria: {listing.get('title', 'Unknown')}")
            except Exception as e:
                logger.debug(f"Error parsing listing item: {e}")
                continue
        
        return listings
    
    def _parse_single_listing(self, item) -> Dict[str, Any]:
        """Parse een enkele advertentie"""
        
        # Listing ID (meerdere mogelijkheden)
        listing_id = (
            item.get('data-item-id') or
            item.get('id', '').replace('listing-', '') or
            self.safe_extract(item, ['[data-item-id]'], 'data-item-id')
        )
        
        # Title (meerdere selectors als fallback)
        title = self.safe_extract(
            item,
            [
                'h3.hz-Listing-title',
                'h2.hz-Listing-title',
                'a.hz-Link--block',
                '.mp-Listing-title',
                '[class*="title"]'
            ]
        )
        
        # URL
        url_element = item.select_one('a.hz-Listing-coverLink, a[href*="/a/"]')
        url = ''
        if url_element:
            url = url_element.get('href', '')
            if url and not url.startswith('http'):
                url = self.BASE_URL + url
        
        # Prijs
        price_text = self.safe_extract(
            item,
            [
                'span.hz-Listing-price',
                'p.hz-Listing-price',
                '.mp-Listing-price',
                '[class*="price"]'
            ]
        )
        price = self.extract_price(price_text)
        
        # Afbeelding
        image_url = self.safe_extract(
            item,
            [
                'img.hz-Listing-coverImage',
                'img[data-src]',
                'img.mp-Listing-image'
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
                'span.hz-Listing-location',
                '.mp-Listing-location',
                '[class*="location"]'
            ]
        )
        
        # Beschrijving (als beschikbaar)
        description = self.safe_extract(
            item,
            [
                'p.hz-Listing-description',
                '.mp-Listing-description',
                '[class*="description"]'
            ]
        )
        
        # Datum
        posted_date = self.safe_extract(
            item,
            [
                'span.hz-Listing-date',
                'time',
                '[class*="date"]'
            ]
        )
        
        return {
            'listing_id': listing_id,
            'title': title,
            'price': price,
            'url': url,
            'image_url': image_url,
            'location': location,
            'description': description,
            'posted_date': posted_date,
            'platform': self.platform_name
        }
