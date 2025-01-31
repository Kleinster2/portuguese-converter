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
        enabled = os.getenv("SPELL_CHECK_ENABLED", "false").lower() == "true"
        api_key = os.getenv("openai_api_key")
        rate_limit = int(os.getenv("SPELL_CHECK_RATE_LIMIT", "60"))
        cache_size = int(os.getenv("SPELL_CHECK_CACHE_SIZE", "1000"))
        cache_ttl = int(os.getenv("SPELL_CHECK_CACHE_TTL", "3600"))
        
        if not api_key:
            logger.warning("No OpenAI API key found, spell checking will be disabled")
            enabled = False
        
        return cls(
            enabled=enabled,
            api_key=api_key,
            rate_limit=rate_limit,
            cache_size=cache_size,
            cache_ttl=cache_ttl
        )
