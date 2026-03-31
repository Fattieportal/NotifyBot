"""
Discord Notifier - Stuur notificaties via Discord Webhook
"""
import logging
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """
    Discord webhook notificatie systeem
    
    Setup:
    1. Ga naar Discord Server Settings
    2. Integrations -> Webhooks
    3. Create Webhook
    4. Kopieer webhook URL
    """
    
    def __init__(self, webhook_url: str):
        """
        Args:
            webhook_url: Discord webhook URL
        """
        self.webhook_url = webhook_url
    
    def send_notification(self, listing: Dict[str, Any]) -> bool:
        """
        Stuur advertentie notificatie via Discord
        
        Args:
            listing: Advertentie data dictionary
        
        Returns:
            True als succesvol verstuurd
        """
        try:
            embed = self._create_embed(listing)
            
            payload = {
                'embeds': [embed]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info("Discord notificatie verzonden")
                return True
            else:
                logger.error(f"Discord webhook error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Discord notificatie error: {e}")
            return False
    
    def _create_embed(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creëer Discord embed voor advertentie
        
        Args:
            listing: Advertentie data
        
        Returns:
            Discord embed dictionary
        """
        platform = listing.get('platform', 'Unknown').upper()
        title = listing.get('title', 'Geen titel')
        price = listing.get('price')
        url = listing.get('url', '')
        location = listing.get('location', 'Onbekend')
        image_url = listing.get('image_url')
        description = listing.get('description', '')
        
        # Format prijs
        price_str = f"€ {price:,.2f}" if price else "Prijs op aanvraag"
        
        # Truncate description
        if description and len(description) > 200:
            description = description[:197] + "..."
        
        embed = {
            'title': f'🚗 {title}',
            'url': url,
            'description': description or 'Nieuwe advertentie gevonden!',
            'color': 3447003,  # Blauw
            'fields': [
                {
                    'name': '💰 Prijs',
                    'value': price_str,
                    'inline': True
                },
                {
                    'name': '📍 Locatie',
                    'value': location,
                    'inline': True
                },
                {
                    'name': '🌐 Platform',
                    'value': platform,
                    'inline': True
                }
            ],
            'footer': {
                'text': 'Notification Bot'
            },
            'timestamp': listing.get('created_at', '')
        }
        
        if image_url:
            embed['thumbnail'] = {'url': image_url}
        
        return embed
    
    def send_test_message(self) -> bool:
        """
        Stuur test bericht
        
        Returns:
            True als test succesvol
        """
        embed = {
            'title': '✅ Notification Bot Test',
            'description': 'De bot is succesvol geconfigureerd!',
            'color': 3066993  # Groen
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json={'embeds': [embed]},
                timeout=10
            )
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Discord test error: {e}")
            return False
