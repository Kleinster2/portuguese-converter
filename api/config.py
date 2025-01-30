from typing import Optional
import os
import logging
from dataclasses import dataclass
import time
import threading

# Load environment variables from .env file

logger = logging.getLogger(__name__)

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
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                logger.error("OPENAI_API_KEY not found in environment variables")
                raise ValueError("OPENAI_API_KEY environment variable is required")

            enabled = os.environ.get('SPELL_CHECK_ENABLED', 'true').lower() == 'true'
            rate_limit = int(os.environ.get('SPELL_CHECK_RATE_LIMIT', '60'))
            cache_size = int(os.environ.get('SPELL_CHECK_CACHE_SIZE', '1000'))
            cache_ttl = int(os.environ.get('SPELL_CHECK_CACHE_TTL', '3600'))

            logger.info("Successfully loaded configuration from environment variables")
            logger.info(f"Spell check enabled: {enabled}")
            logger.info(f"Rate limit: {rate_limit}")
            logger.info(f"Cache size: {cache_size}")
            logger.info(f"Cache TTL: {cache_ttl}")

            return cls(
                api_key=api_key,
                enabled=enabled,
                rate_limit=rate_limit,
                cache_size=cache_size,
                cache_ttl=cache_ttl
            )
        except ValueError as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {str(e)}")
            raise ValueError(f"Failed to load configuration: {str(e)}")

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
            # Remove requests older than 1 minute
            cutoff_time = current_time - 60
            self._request_times = [t for t in self._request_times if t > cutoff_time]
            
            # Check if we're within the rate limit
            if len(self._request_times) >= self.rate_limit:
                return False
                
            # Add current request
            self._request_times.append(current_time)
            return True
