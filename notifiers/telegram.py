"""
Telegram Notifier - Stuur notificaties via Telegram Bot

Meest aanbevolen methode omdat:
- Instant notifications
- Geen email spam folders
- Gratis en betrouwbaar
- Support voor images en links
"""
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Telegram notificatie systeem
    
    Setup:
    1. Praat met @BotFather op Telegram
    2. Gebruik /newbot commando
    3. Krijg bot token
    4. Start chat met je bot
    5. Krijg chat_id via: https://api.telegram.org/bot<TOKEN>/getUpdates
    """
    
    def __init__(self, bot_token: str, chat_id: str, include_image: bool = True):
        """
        Args:
            bot_token: Telegram bot token van BotFather
            chat_id: Je Telegram chat ID
            include_image: Include afbeelding in notificatie
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.include_image = include_image
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        
        # Verificeer credentials
        if not self._verify_connection():
            logger.warning("Telegram verificatie gefaald - check credentials")
    
    def _verify_connection(self) -> bool:
        """Verificeer Telegram bot connectie"""
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"Telegram bot verbonden: @{bot_info['result']['username']}")
                return True
            return False
        except Exception as e:
            logger.error(f"Telegram verificatie error: {e}")
            return False
    
    def send_notification(self, listing: Dict[str, Any]) -> bool:
        """
        Stuur advertentie notificatie via Telegram
        
        Args:
            listing: Advertentie data dictionary
        
        Returns:
            True als succesvol verstuurd
        """
        try:
            # Format bericht
            message = self._format_message(listing)
            
            # Stuur met of zonder afbeelding
            if self.include_image and listing.get('image_url'):
                return self._send_photo(listing['image_url'], message)
            else:
                return self._send_text(message)
                
        except Exception as e:
            logger.error(f"Telegram notificatie error: {e}")
            return False
    
    def _format_message(self, listing: Dict[str, Any]) -> str:
        """
        Format advertentie als Telegram message (HTML)
        
        Args:
            listing: Advertentie data
        
        Returns:
            Formatted HTML message
        """
        platform = listing.get('platform', 'Unknown').upper()
        title = listing.get('title', 'Geen titel')
        price = listing.get('price')
        url = listing.get('url', '')
        location = listing.get('location', 'Onbekend')
        posted_date = listing.get('posted_date', 'Onbekend')
        
        # Format prijs
        price_str = f"€ {price:,.2f}" if price else "Prijs op aanvraag"
        
        # Build message
        message = f"🚗 <b>Nieuwe Advertentie - {platform}</b>\n\n"
        message += f"<b>{title}</b>\n\n"
        message += f"💰 <b>Prijs:</b> {price_str}\n"
        message += f"📍 <b>Locatie:</b> {location}\n"
        message += f"📅 <b>Geplaatst:</b> {posted_date}\n\n"
        message += f"🔗 <a href='{url}'>Bekijk advertentie</a>"
        
        return message
    
    def _send_text(self, message: str) -> bool:
        """Stuur text bericht"""
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram notificatie verzonden")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
    
    def _send_photo(self, image_url: str, caption: str) -> bool:
        """Stuur foto met caption"""
        try:
            url = f"{self.api_url}/sendPhoto"
            payload = {
                'chat_id': self.chat_id,
                'photo': image_url,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                logger.info("Telegram notificatie met foto verzonden")
                return True
            else:
                # Fallback naar text als foto faalt
                logger.warning(f"Foto verzenden gefaald, fallback naar text")
                return self._send_text(caption)
                
        except Exception as e:
            logger.error(f"Telegram photo send error: {e}")
            # Fallback naar text
            return self._send_text(caption)
    
    def send_test_message(self) -> bool:
        """
        Stuur test bericht om setup te verifiëren
        
        Returns:
            True als test succesvol
        """
        test_message = "✅ <b>Notification Bot Test</b>\n\nDe bot is succesvol geconfigureerd!"
        return self._send_text(test_message)
