"""
Email Notifier - Stuur notificaties via Email
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Email notificatie systeem via SMTP
    
    Setup voor Gmail:
    1. Enable 2-factor authentication
    2. Generate App Password: https://myaccount.google.com/apppasswords
    3. Gebruik App Password in config
    """
    
    def __init__(self, smtp_server: str, smtp_port: int, 
                 sender_email: str, sender_password: str,
                 recipient_email: str, use_tls: bool = True):
        """
        Args:
            smtp_server: SMTP server adres
            smtp_port: SMTP poort (587 voor TLS, 465 voor SSL)
            sender_email: Sender email adres
            sender_password: Sender email wachtwoord/app password
            recipient_email: Recipient email adres
            use_tls: Gebruik TLS (True voor Gmail)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        self.use_tls = use_tls
    
    def send_notification(self, listing: Dict[str, Any]) -> bool:
        """
        Stuur advertentie notificatie via email
        
        Args:
            listing: Advertentie data dictionary
        
        Returns:
            True als succesvol verstuurd
        """
        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self._create_subject(listing)
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # HTML body
            html_body = self._create_html_body(listing)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Verstuur
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email notificatie verzonden naar {self.recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email notificatie error: {e}")
            return False
    
    def _create_subject(self, listing: Dict[str, Any]) -> str:
        """Create email subject"""
        platform = listing.get('platform', 'Unknown').upper()
        title = listing.get('title', 'Nieuwe advertentie')
        price = listing.get('price')
        
        if price:
            return f"🚗 {platform}: {title} - €{price:,.0f}"
        return f"🚗 {platform}: {title}"
    
    def _create_html_body(self, listing: Dict[str, Any]) -> str:
        """
        Create HTML email body
        
        Args:
            listing: Advertentie data
        
        Returns:
            HTML string
        """
        platform = listing.get('platform', 'Unknown').upper()
        title = listing.get('title', 'Geen titel')
        price = listing.get('price')
        url = listing.get('url', '#')
        location = listing.get('location', 'Onbekend')
        image_url = listing.get('image_url', '')
        description = listing.get('description', '')
        posted_date = listing.get('posted_date', 'Onbekend')
        
        # Format prijs
        price_str = f"€ {price:,.2f}" if price else "Prijs op aanvraag"
        
        # Build HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .info-row {{ margin: 10px 0; padding: 10px; background: white; border-left: 3px solid #4CAF50; }}
                .label {{ font-weight: bold; color: #666; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #4CAF50; 
                           color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .image {{ max-width: 100%; height: auto; margin: 10px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚗 Nieuwe Advertentie - {platform}</h1>
                </div>
                <div class="content">
                    <h2>{title}</h2>
        """
        
        if image_url:
            html += f'<img src="{image_url}" alt="Advertentie foto" class="image">'
        
        html += f"""
                    <div class="info-row">
                        <span class="label">💰 Prijs:</span> {price_str}
                    </div>
                    <div class="info-row">
                        <span class="label">📍 Locatie:</span> {location}
                    </div>
                    <div class="info-row">
                        <span class="label">📅 Geplaatst:</span> {posted_date}
                    </div>
        """
        
        if description:
            html += f"""
                    <div class="info-row">
                        <span class="label">📝 Beschrijving:</span><br>
                        {description[:300]}{'...' if len(description) > 300 else ''}
                    </div>
            """
        
        html += f"""
                    <center>
                        <a href="{url}" class="button">Bekijk Advertentie</a>
                    </center>
                </div>
                <div class="footer">
                    <p>Dit is een geautomatiseerde notificatie van de Notification Bot</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_test_message(self) -> bool:
        """
        Stuur test email
        
        Returns:
            True als test succesvol
        """
        test_listing = {
            'platform': 'TEST',
            'title': 'Test Advertentie',
            'price': 12345.67,
            'url': 'https://example.com',
            'location': 'Test Locatie',
            'description': 'Dit is een test notificatie om de email configuratie te verifiëren.',
            'posted_date': 'Nu'
        }
        
        return self.send_notification(test_listing)
