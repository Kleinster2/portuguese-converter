import os
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class SpellCheckConfig:
    enabled: bool = False
    api_key: Optional[str] = None
    rate_limit: int = 60  # requests per minute
    cache_size: int = 1000  # number of items
    cache_ttl: int = 3600  # seconds

    @classmethod
    def from_env(cls) -> 'SpellCheckConfig':
        """Create config from environment variables."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            logger.info("Loaded environment variables from .env file")
        except ImportError:
            logger.warning("python-dotenv not available, using OS environment variables")

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
