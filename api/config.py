from typing import Optional, List
import os
import logging
from dataclasses import dataclass, field
import time
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Try to load environment variables from .env, but don't fail if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except ImportError:
    logger.warning("python-dotenv not available, using OS environment variables")

@dataclass
class SpellCheckConfig:
    enabled: bool = False
    api_key: Optional[str] = None
    rate_limit: int = 60  # requests per minute
    cache_size: int = 1000  # number of items
    cache_ttl: int = 3600  # seconds
    _request_times: List[float] = field(default_factory=list)
    _rate_limit_lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self):
        pass

    @classmethod
    def from_env(cls) -> 'SpellCheckConfig':
        """Create config from environment variables."""
        enabled_str = os.getenv('SPELL_CHECK_ENABLED', 'false').lower()
        enabled = enabled_str == 'true'
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key and enabled:
            logger.warning("OpenAI API key not found, disabling spell check")
            enabled = False
        
        return cls(
            enabled=enabled,
            api_key=api_key,
            rate_limit=int(os.getenv('SPELL_CHECK_RATE_LIMIT', '60')),
            cache_size=int(os.getenv('SPELL_CHECK_CACHE_SIZE', '1000')),
            cache_ttl=int(os.getenv('SPELL_CHECK_CACHE_TTL', '3600'))
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
            # Remove requests older than 1 minute
            cutoff_time = current_time - 60
            self._request_times = [t for t in self._request_times if t > cutoff_time]
            
            # Check if we're within the rate limit
            if len(self._request_times) >= self.rate_limit:
                return False
                
            # Add current request
            self._request_times.append(current_time)
            return True
