"""
Rate Limiter - OPLOSSING VOOR TECHNISCHE UITDAGING #1: Rate Limiting

Deze module implementeert:
- Per-domain rate limiting
- Random delays tussen requests
- Exponential backoff bij errors
- Request throttling
"""
import time
import random
from collections import defaultdict
from threading import Lock
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter met exponential backoff en per-domain throttling
    
    Voorkomt IP blocking door:
    1. Minimale delay tussen requests
    2. Random jitter voor natuurlijk gedrag
    3. Per-domain tracking
    4. Exponential backoff bij failures
    """
    
    def __init__(self, 
                 min_delay: float = 3.0,
                 max_delay: float = 10.0,
                 max_retries: int = 3):
        """
        Args:
            min_delay: Minimale seconden tussen requests
            max_delay: Maximale seconden tussen requests
            max_retries: Maximale retry pogingen
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        
        # Track laatste request tijd per domain
        self._last_request_time: Dict[str, float] = defaultdict(float)
        self._lock = Lock()
        
        # Track failures voor exponential backoff
        self._failure_count: Dict[str, int] = defaultdict(int)
        
        logger.info(f"RateLimiter geïnitialiseerd: {min_delay}s - {max_delay}s delay")
    
    def wait(self, domain: str) -> None:
        """
        Wacht de juiste tijd voordat een request naar domain gedaan wordt
        
        Args:
            domain: Domain naam (bijv. 'marktplaats.nl')
        """
        with self._lock:
            now = time.time()
            last_request = self._last_request_time[domain]
            
            # Bereken hoe lang we al gewacht hebben
            elapsed = now - last_request
            
            # Bereken random delay (voor natuurlijk gedrag)
            base_delay = random.uniform(self.min_delay, self.max_delay)
            
            # Exponential backoff bij failures
            failure_multiplier = 2 ** self._failure_count[domain]
            total_delay = base_delay * failure_multiplier
            
            # Cap de maximum delay
            total_delay = min(total_delay, 60.0)  # Max 60 seconden
            
            # Wacht alleen als nodig
            if elapsed < total_delay:
                wait_time = total_delay - elapsed
                logger.debug(f"Rate limiting {domain}: wachten {wait_time:.2f}s")
                time.sleep(wait_time)
            
            # Update laatste request tijd
            self._last_request_time[domain] = time.time()
    
    def mark_success(self, domain: str) -> None:
        """
        Markeer een succesvolle request - reset failure counter
        
        Args:
            domain: Domain naam
        """
        with self._lock:
            if domain in self._failure_count:
                logger.debug(f"Reset failure count voor {domain}")
                self._failure_count[domain] = 0
    
    def mark_failure(self, domain: str) -> bool:
        """
        Markeer een gefaalde request - increment failure counter
        
        Args:
            domain: Domain naam
        
        Returns:
            True als we moeten retries, False als max retries bereikt
        """
        with self._lock:
            self._failure_count[domain] += 1
            count = self._failure_count[domain]
            
            if count >= self.max_retries:
                logger.warning(f"Max retries ({self.max_retries}) bereikt voor {domain}")
                return False
            
            logger.info(f"Failure #{count} voor {domain}, exponential backoff actief")
            return True
    
    def reset(self, domain: str = None) -> None:
        """
        Reset de rate limiter
        
        Args:
            domain: Specifieke domain of None voor alle domains
        """
        with self._lock:
            if domain:
                self._last_request_time.pop(domain, None)
                self._failure_count.pop(domain, None)
                logger.debug(f"Rate limiter reset voor {domain}")
            else:
                self._last_request_time.clear()
                self._failure_count.clear()
                logger.debug("Rate limiter volledig gereset")
    
    def get_stats(self) -> Dict[str, Dict]:
        """
        Krijg statistieken per domain
        
        Returns:
            Dictionary met stats per domain
        """
        with self._lock:
            stats = {}
            for domain in set(list(self._last_request_time.keys()) + 
                            list(self._failure_count.keys())):
                stats[domain] = {
                    'last_request': self._last_request_time.get(domain, 0),
                    'failures': self._failure_count.get(domain, 0),
                    'time_since_last': time.time() - self._last_request_time.get(domain, 0)
                }
            return stats
