"""
Database Manager - OPLOSSING VOOR TECHNISCHE UITDAGING #5: Duplicate Prevention

Deze module implementeert:
- SQLite database voor listings
- Unique ID tracking per advertentie
- Content hash voor duplicate detectie
- Timestamp tracking
- Auto cleanup van oude entries
"""
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database manager voor advertenties met duplicate detectie
    
    Voorkomt duplicaten door:
    1. Unique listing_id per platform
    2. Content hash voor vergelijking
    3. Timestamp tracking
    4. Efficiënte queries
    """
    
    def __init__(self, db_path: str = "data/listings.db"):
        """
        Args:
            db_path: Pad naar SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        logger.info(f"Database geïnitialiseerd: {self.db_path}")
    
    def _init_database(self) -> None:
        """Initialiseer database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Listings tabel
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    listing_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    price REAL,
                    url TEXT NOT NULL,
                    image_url TEXT,
                    description TEXT,
                    location TEXT,
                    posted_date TEXT,
                    content_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notified BOOLEAN DEFAULT 0,
                    UNIQUE(platform, listing_id)
                )
            """)
            
            # Indices voor snelle queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_platform_listing 
                ON listings(platform, listing_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_hash 
                ON listings(content_hash)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON listings(created_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notified 
                ON listings(notified)
            """)
            
            # Metadata tabel voor statistieken
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.debug("Database schema geverifieerd")
    
    @staticmethod
    def _generate_hash(data: Dict[str, Any]) -> str:
        """
        Genereer een hash van advertentie content voor duplicate detectie
        
        Args:
            data: Dictionary met advertentie data
        
        Returns:
            SHA256 hash string
        """
        # Gebruik relevante fields voor hash
        hash_data = {
            'title': data.get('title', '').lower().strip(),
            'price': data.get('price', 0),
            'url': data.get('url', '').lower().strip(),
        }
        
        # Sorteer voor consistentie
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def is_duplicate(self, platform: str, listing_id: str, data: Dict[str, Any]) -> bool:
        """
        Check of een advertentie al bestaat in database
        
        Args:
            platform: Platform naam
            listing_id: Unique ID van de advertentie
            data: Advertentie data
        
        Returns:
            True als duplicate, False als nieuw
        """
        content_hash = self._generate_hash(data)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check op listing_id OF content_hash
            cursor.execute("""
                SELECT COUNT(*) FROM listings 
                WHERE (platform = ? AND listing_id = ?) 
                   OR content_hash = ?
            """, (platform, listing_id, content_hash))
            
            count = cursor.fetchone()[0]
            return count > 0
    
    def add_listing(self, platform: str, listing_id: str, data: Dict[str, Any]) -> bool:
        """
        Voeg nieuwe advertentie toe aan database
        
        Args:
            platform: Platform naam
            listing_id: Unique ID van de advertentie
            data: Advertentie data (title, price, url, etc.)
        
        Returns:
            True als succesvol toegevoegd, False als duplicate
        """
        if self.is_duplicate(platform, listing_id, data):
            logger.debug(f"Duplicate gevonden: {platform}/{listing_id}")
            return False
        
        content_hash = self._generate_hash(data)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO listings 
                    (platform, listing_id, title, price, url, image_url, 
                     description, location, posted_date, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    platform,
                    listing_id,
                    data.get('title', ''),
                    data.get('price'),
                    data.get('url', ''),
                    data.get('image_url'),
                    data.get('description'),
                    data.get('location'),
                    data.get('posted_date'),
                    content_hash
                ))
                
                conn.commit()
                logger.info(f"Nieuwe advertentie toegevoegd: {platform}/{listing_id}")
                return True
                
        except sqlite3.IntegrityError as e:
            logger.warning(f"Duplicate constraint violation: {e}")
            return False
    
    def mark_as_notified(self, platform: str, listing_id: str) -> None:
        """
        Markeer advertentie als genotificeerd
        
        Args:
            platform: Platform naam
            listing_id: Unique ID van de advertentie
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE listings 
                SET notified = 1 
                WHERE platform = ? AND listing_id = ?
            """, (platform, listing_id))
            conn.commit()
    
    def get_unnotified_listings(self, platform: str = None) -> List[Dict[str, Any]]:
        """
        Krijg alle advertenties die nog niet genotificeerd zijn
        
        Args:
            platform: Filter op specifiek platform (optioneel)
        
        Returns:
            List van advertentie dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if platform:
                cursor.execute("""
                    SELECT * FROM listings 
                    WHERE platform = ? AND notified = 0
                    ORDER BY created_at DESC
                """, (platform,))
            else:
                cursor.execute("""
                    SELECT * FROM listings 
                    WHERE notified = 0
                    ORDER BY created_at DESC
                """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def cleanup_old_listings(self, days: int = 30) -> int:
        """
        Verwijder oude advertenties uit database
        
        Args:
            days: Verwijder entries ouder dan X dagen
        
        Returns:
            Aantal verwijderde entries
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM listings 
                WHERE created_at < ? AND notified = 1
            """, (cutoff_date.isoformat(),))
            
            deleted = cursor.rowcount
            conn.commit()
            
            if deleted > 0:
                logger.info(f"Opgeschoond: {deleted} oude advertenties verwijderd")
            
            return deleted
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Krijg database statistieken
        
        Returns:
            Dictionary met stats
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Totaal aantal listings
            cursor.execute("SELECT COUNT(*) FROM listings")
            total = cursor.fetchone()[0]
            
            # Per platform
            cursor.execute("""
                SELECT platform, COUNT(*) as count 
                FROM listings 
                GROUP BY platform
            """)
            per_platform = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Notified vs unnotified
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN notified = 1 THEN 1 ELSE 0 END) as notified,
                    SUM(CASE WHEN notified = 0 THEN 1 ELSE 0 END) as pending
                FROM listings
            """)
            notified, pending = cursor.fetchone()
            
            # Laatste 24 uur
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM listings 
                WHERE created_at > ?
            """, (yesterday,))
            last_24h = cursor.fetchone()[0]
            
            return {
                'total_listings': total,
                'per_platform': per_platform,
                'notified': notified or 0,
                'pending': pending or 0,
                'last_24h': last_24h
            }
