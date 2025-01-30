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
    enabled: bool = True
    rate_limit: int = 60  # requests per minute
    cache_size: int = 1000  # number of items to cache
    cache_ttl: int = 3600  # cache time-to-live in seconds
    api_key: Optional[str] = None
    
    # Rate limiting - use field(default_factory=...) for mutable defaults
    _request_times: List[float] = field(default_factory=list)
    _rate_limit_lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self):
        # No longer needed since we're using field(default_factory=...)
        pass

    @classmethod
    def from_env(cls) -> 'SpellCheckConfig':
        """Create config from environment variables."""
        try:
            # Log all non-sensitive environment variables
            env_vars = {k: '***' if k == 'OPENAI_API_KEY' else v 
                       for k, v in os.environ.items() 
                       if k.startswith('SPELL_CHECK_') or k == 'OPENAI_API_KEY'}
            logger.info(f"Environment variables: {env_vars}")

            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OPENAI_API_KEY not found - spellcheck will be disabled")
                return cls(enabled=False, api_key=None)

            enabled = os.getenv('SPELL_CHECK_ENABLED', 'true').lower() == 'true'
            rate_limit = int(os.getenv('SPELL_CHECK_RATE_LIMIT', '60'))
            cache_size = int(os.getenv('SPELL_CHECK_CACHE_SIZE', '1000'))
            cache_ttl = int(os.getenv('SPELL_CHECK_CACHE_TTL', '3600'))

            logger.info("Successfully loaded configuration from environment variables")
            logger.info(f"Spell check enabled: {enabled}")
            return cls(
                enabled=enabled,
                rate_limit=rate_limit,
                cache_size=cache_size,
                cache_ttl=cache_ttl,
                api_key=api_key
            )
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            logger.warning("Using default configuration with spellcheck disabled")
            return cls(enabled=False, api_key=None)

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
