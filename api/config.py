from typing import Optional
import os
from dataclasses import dataclass
from dotenv import load_dotenv
import time
import threading

# Load environment variables from .env file
load_dotenv()

@dataclass
class SpellCheckConfig:
    enabled: bool = True
    rate_limit: int = 60  # requests per minute
    cache_size: int = 1000  # number of items to cache
    cache_ttl: int = 3600  # cache time-to-live in seconds
    api_key: Optional[str] = None
    
    # Rate limiting
    _request_times: list = None
    _rate_limit_lock: threading.Lock = None

    def __post_init__(self):
        self._request_times = []
        self._rate_limit_lock = threading.Lock()

    @classmethod
    def from_env(cls) -> 'SpellCheckConfig':
        """Create config from environment variables."""
        return cls(
            enabled=os.getenv('SPELL_CHECK_ENABLED', 'true').lower() == 'true',
            rate_limit=int(os.getenv('SPELL_CHECK_RATE_LIMIT', '60')),
            cache_size=int(os.getenv('SPELL_CHECK_CACHE_SIZE', '1000')),
            cache_ttl=int(os.getenv('SPELL_CHECK_CACHE_TTL', '3600')),
            api_key=os.getenv('OPENAI_API_KEY')
        )

    def to_dict(self) -> dict:
        """Convert config to dictionary, excluding sensitive data."""
        return {
            'enabled': self.enabled,
            'rate_limit': self.rate_limit,
            'cache_size': self.cache_size,
            'cache_ttl': self.cache_ttl,
            'api_available': bool(self.api_key)
        }

    def is_within_rate_limit(self) -> bool:
        """Check if we're within the rate limit."""
        with self._rate_limit_lock:
            current_time = time.time()
            # Remove requests older than 60 seconds
            self._request_times = [t for t in self._request_times 
                                 if current_time - t <= 60]
            
            if len(self._request_times) >= self.rate_limit:
                return False
            
            self._request_times.append(current_time)
            return True
