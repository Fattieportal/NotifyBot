"""
Multi-Platform Notification Bot
Main Entry Point

Integreert:
- Meerdere scrapers
- Database management
- Notificatie systemen
- Scheduling
- Error handling
"""
import logging
import time
import yaml
import schedule
from pathlib import Path
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

from utils.logger import setup_logger
from utils.rate_limiter import RateLimiter
from database.db_manager import DatabaseManager
from notifiers.telegram import TelegramNotifier
from notifiers.email import EmailNotifier
from notifiers.discord import DiscordNotifier
from scrapers.marktplaats import MarktplaatsScraper
from scrapers.autoscout import AutoScoutScraper
from scrapers.mobile_de import MobileDeScraper
from scrapers.facebook import FacebookScraper
from scrapers.ebay_kleinanzeigen import EbayKleinanzeigenScraper

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger('NotificationBot', 'logs/bot.log', 'INFO')


class NotificationBot:
    """
    Main bot class die alles coördineert
    
    Features:
    - Multi-platform scraping
    - Duplicate detectie
    - Multiple notificatie methodes
    - Scheduled execution
    - Error recovery
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize bot met configuratie
        
        Args:
            config_path: Pad naar YAML config file
        """
        logger.info("="*60)
        logger.info("🚀 Notification Bot Starting...")
        logger.info("="*60)
        
        # Load config
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.db = DatabaseManager(self.config['database']['path'])
        
        self.rate_limiter = RateLimiter(
            min_delay=self.config['anti_detection']['random_delay_min'],
            max_delay=self.config['anti_detection']['random_delay_max'],
            max_retries=self.config['global']['max_retries']
        )
        
        # Initialize notifiers
        self.notifiers = self._init_notifiers()
        
        # Initialize scrapers
        self.scrapers = self._init_scrapers()
        
        logger.info(f"✓ Bot geïnitialiseerd met {len(self.scrapers)} scrapers en {len(self.notifiers)} notifiers")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load YAML configuratie"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"✓ Configuratie geladen: {config_path}")
            return config
            
        except FileNotFoundError:
            logger.error(f"❌ Config file niet gevonden: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"❌ Config parse error: {e}")
            raise
    
    def _init_notifiers(self) -> List:
        """Initialiseer notificatie systemen"""
        notifiers = []
        notif_config = self.config['notifications']
        
        # Telegram
        if notif_config.get('telegram', {}).get('enabled'):
            try:
                token = os.getenv('TELEGRAM_BOT_TOKEN') or notif_config['telegram']['bot_token']
                chat_id = os.getenv('TELEGRAM_CHAT_ID') or notif_config['telegram']['chat_id']
                
                telegram = TelegramNotifier(
                    bot_token=token,
                    chat_id=chat_id,
                    include_image=notif_config['telegram'].get('include_image', True)
                )
                notifiers.append(telegram)
                logger.info("✓ Telegram notifier geactiveerd")
            except Exception as e:
                logger.error(f"❌ Telegram init failed: {e}")
        
        # Discord
        if notif_config.get('discord', {}).get('enabled'):
            try:
                webhook_url = os.getenv('DISCORD_WEBHOOK_URL') or notif_config['discord']['webhook_url']
                
                discord = DiscordNotifier(webhook_url=webhook_url)
                notifiers.append(discord)
                logger.info("✓ Discord notifier geactiveerd")
            except Exception as e:
                logger.error(f"❌ Discord init failed: {e}")
        
        # Email
        if notif_config.get('email', {}).get('enabled'):
            try:
                email = EmailNotifier(
                    smtp_server=notif_config['email']['smtp_server'],
                    smtp_port=notif_config['email']['smtp_port'],
                    sender_email=os.getenv('EMAIL_SENDER') or notif_config['email']['sender_email'],
                    sender_password=os.getenv('EMAIL_PASSWORD') or notif_config['email']['sender_password'],
                    recipient_email=os.getenv('EMAIL_RECIPIENT') or notif_config['email']['recipient_email'],
                    use_tls=notif_config['email'].get('use_tls', True)
                )
                notifiers.append(email)
                logger.info("✓ Email notifier geactiveerd")
            except Exception as e:
                logger.error(f"❌ Email init failed: {e}")
        
        if not notifiers:
            logger.warning("⚠️ Geen notifiers geactiveerd!")
        
        return notifiers
    
    def _init_scrapers(self) -> Dict[str, Any]:
        """Initialiseer platform scrapers"""
        scrapers = {}
        platforms_config = self.config['platforms']
        
        # Marktplaats
        if platforms_config.get('marktplaats', {}).get('enabled'):
            scrapers['marktplaats'] = MarktplaatsScraper(
                criteria=platforms_config['marktplaats']['criteria'],
                db_manager=self.db,
                rate_limiter=self.rate_limiter,
                platform_name='marktplaats'
            )
            logger.info("✓ Marktplaats scraper geactiveerd")
        
        # AutoScout
        if platforms_config.get('autoscout', {}).get('enabled'):
            scrapers['autoscout'] = AutoScoutScraper(
                criteria=platforms_config['autoscout']['criteria'],
                db_manager=self.db,
                rate_limiter=self.rate_limiter,
                platform_name='autoscout'
            )
            logger.info("✓ AutoScout scraper geactiveerd")
        
        # Mobile.de
        if platforms_config.get('mobile_de', {}).get('enabled'):
            scrapers['mobile_de'] = MobileDeScraper(
                criteria=platforms_config['mobile_de']['criteria'],
                db_manager=self.db,
                rate_limiter=self.rate_limiter,
                platform_name='mobile_de'
            )
            logger.info("✓ Mobile.de scraper geactiveerd")
        
        # Facebook
        if platforms_config.get('facebook', {}).get('enabled'):
            fb_config = platforms_config['facebook']
            scrapers['facebook'] = FacebookScraper(
                criteria=fb_config['criteria'],
                db_manager=self.db,
                rate_limiter=self.rate_limiter,
                platform_name='facebook',
                headless=self.config['anti_detection'].get('headless_browser', True),
                email=os.getenv('FACEBOOK_EMAIL') or fb_config.get('credentials', {}).get('email'),
                password=os.getenv('FACEBOOK_PASSWORD') or fb_config.get('credentials', {}).get('password')
            )
            logger.info("✓ Facebook scraper geactiveerd (experimental)")
        
        # eBay Kleinanzeigen
        if platforms_config.get('ebay_kleinanzeigen', {}).get('enabled'):
            scrapers['ebay_kleinanzeigen'] = EbayKleinanzeigenScraper(
                criteria=platforms_config['ebay_kleinanzeigen']['criteria'],
                db_manager=self.db,
                rate_limiter=self.rate_limiter,
                platform_name='ebay_kleinanzeigen'
            )
            logger.info("✓ eBay Kleinanzeigen scraper geactiveerd")
        
        if not scrapers:
            logger.warning("⚠️ Geen scrapers geactiveerd!")
        
        return scrapers
    
    def scrape_all_platforms(self):
        """
        Scrape alle geactiveerde platforms en stuur notificaties
        """
        logger.info("\n" + "="*60)
        logger.info("🔍 Starting scrape cycle...")
        logger.info("="*60)
        
        total_new = 0
        
        for platform_name, scraper in self.scrapers.items():
            try:
                logger.info(f"\n📡 Scraping {platform_name.upper()}...")
                
                # Scrape platform
                new_listings = scraper.scrape()
                
                if new_listings:
                    logger.info(f"✨ {len(new_listings)} nieuwe advertenties gevonden op {platform_name}")
                    
                    # Stuur notificaties
                    for listing in new_listings:
                        self._send_notifications(listing)
                        
                        # Mark as notified
                        self.db.mark_as_notified(platform_name, listing['listing_id'])
                    
                    total_new += len(new_listings)
                else:
                    logger.info(f"ℹ️ Geen nieuwe advertenties op {platform_name}")
                
            except Exception as e:
                logger.error(f"❌ Error scraping {platform_name}: {e}", exc_info=True)
                continue
        
        # Statistieken
        stats = self.db.get_statistics()
        
        logger.info("\n" + "="*60)
        logger.info("📊 Scrape Cycle Complete")
        logger.info("="*60)
        logger.info(f"Nieuwe advertenties deze cycle: {total_new}")
        logger.info(f"Totaal in database: {stats['total_listings']}")
        logger.info(f"Laatste 24 uur: {stats['last_24h']}")
        logger.info(f"Pending notificaties: {stats['pending']}")
        logger.info("="*60 + "\n")
    
    def _send_notifications(self, listing: Dict[str, Any]):
        """
        Stuur notificatie via alle geactiveerde notifiers
        
        Args:
            listing: Advertentie data
        """
        platform = listing.get('platform', 'Unknown')
        title = listing.get('title', 'Unknown')
        
        for notifier in self.notifiers:
            try:
                success = notifier.send_notification(listing)
                if success:
                    logger.info(f"✓ Notificatie verzonden via {notifier.__class__.__name__}")
                else:
                    logger.warning(f"⚠️ Notificatie failed via {notifier.__class__.__name__}")
                    
            except Exception as e:
                logger.error(f"❌ Notification error ({notifier.__class__.__name__}): {e}")
    
    def cleanup_old_listings(self):
        """Cleanup oude advertenties uit database"""
        cleanup_days = self.config['database'].get('cleanup_days', 30)
        deleted = self.db.cleanup_old_listings(cleanup_days)
        
        if deleted > 0:
            logger.info(f"🧹 Database cleanup: {deleted} oude entries verwijderd")
    
    def run_once(self):
        """Run één scrape cycle"""
        self.scrape_all_platforms()
        self.cleanup_old_listings()
    
    def run_scheduled(self):
        """
        Run bot met scheduling
        
        Controleert volgens configured intervals
        """
        # Global interval
        interval = self.config['global'].get('check_interval_minutes', 15)
        
        # Schedule scrape job
        schedule.every(interval).minutes.do(self.scrape_all_platforms)
        
        # Schedule daily cleanup
        schedule.every().day.at("03:00").do(self.cleanup_old_listings)
        
        logger.info(f"⏰ Scheduler gestart: scrape elke {interval} minuten")
        logger.info("💡 Tip: Gebruik CTRL+C om te stoppen")
        
        # Run once immediately
        self.scrape_all_platforms()
        
        # Schedule loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check elke minuut
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot gestopt door gebruiker")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}", exc_info=True)
    
    def test_notifications(self):
        """Test alle notificatie systemen"""
        logger.info("🧪 Testing notification systems...")
        
        for notifier in self.notifiers:
            try:
                logger.info(f"Testing {notifier.__class__.__name__}...")
                success = notifier.send_test_message()
                
                if success:
                    logger.info(f"✓ {notifier.__class__.__name__} test passed")
                else:
                    logger.error(f"❌ {notifier.__class__.__name__} test failed")
                    
            except Exception as e:
                logger.error(f"❌ Test error ({notifier.__class__.__name__}): {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Platform Notification Bot')
    parser.add_argument('--config', default='config.yaml', help='Pad naar config file')
    parser.add_argument('--once', action='store_true', help='Run eenmalig (geen scheduling)')
    parser.add_argument('--test', action='store_true', help='Test notificatie systemen')
    parser.add_argument('--stats', action='store_true', help='Toon database statistieken')
    
    args = parser.parse_args()
    
    try:
        # Initialize bot
        bot = NotificationBot(config_path=args.config)
        
        if args.test:
            # Test mode
            bot.test_notifications()
            
        elif args.stats:
            # Stats mode
            stats = bot.db.get_statistics()
            print("\n" + "="*60)
            print("📊 DATABASE STATISTIEKEN")
            print("="*60)
            print(f"Totaal advertenties: {stats['total_listings']}")
            print(f"Laatste 24 uur: {stats['last_24h']}")
            print(f"Genotificeerd: {stats['notified']}")
            print(f"Pending: {stats['pending']}")
            print("\nPer platform:")
            for platform, count in stats['per_platform'].items():
                print(f"  - {platform}: {count}")
            print("="*60 + "\n")
            
        elif args.once:
            # Run once mode
            bot.run_once()
            
        else:
            # Scheduled mode (default)
            bot.run_scheduled()
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot gestopt door gebruiker")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
