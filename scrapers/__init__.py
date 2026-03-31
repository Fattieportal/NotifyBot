"""
Scrapers package - platform-specifieke scrapers
"""
from .base_scraper import BaseScraper
from .marktplaats import MarktplaatsScraper
from .autoscout import AutoScoutScraper
from .mobile_de import MobileDeScraper
from .facebook import FacebookScraper
from .ebay_kleinanzeigen import EbayKleinanzeigenScraper

__all__ = [
    'BaseScraper',
    'MarktplaatsScraper',
    'AutoScoutScraper',
    'MobileDeScraper',
    'FacebookScraper',
    'EbayKleinanzeigenScraper'
]
