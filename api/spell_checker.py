import os
from typing import Optional
import logging
import asyncio
from openai import OpenAI
from openai import APIError as OpenAIAPIError
from cache import TTLCache
from config import SpellCheckConfig

class SpellCheckError(Exception):
    """Base class for spell checker errors."""
    pass

class APIError(SpellCheckError):
    """Raised when there is an error with the OpenAI API."""
    def __init__(self, status_code: int, message: str):
        self.status = status_code  # Keep this for backward compatibility
        self.status_code = status_code
        super().__init__(f"API error {status_code}: {message}")

class RateLimitError(SpellCheckError):
    """Raised when rate limit is exceeded."""
    pass

class SpellChecker:
    """A spell checker that uses OpenAI's API to correct Portuguese text."""
    
    system_prompt = """You are a Portuguese spell checker and grammar corrector. Your task is to correct any spelling or grammar mistakes in the input text while preserving its meaning. Only make corrections that are necessary - if the text is already correct, return it as is. Do not add any explanations or comments, just return the corrected text."""
    
    def __init__(self, config: Optional[SpellCheckConfig] = None):
        """Initialize spell checker with configuration."""
        self.config = config or SpellCheckConfig.from_env()
        if not self.config.api_key:
            raise ValueError("OpenAI API key must be provided in config or OPENAI_API_KEY environment variable")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.config.api_key)
        
        # Initialize cache
        self.cache = TTLCache(
            max_size=self.config.cache_size,
            ttl=self.config.cache_ttl
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Spell checker initialized")

    async def correct(self, text: str) -> str:
        """Correct spelling and grammar in the given text."""
        self.logger.info(f"Correcting text: {text}")
        if not text:
            return text
        
        # Check cache first
        if text in self.cache:
            self.logger.info("Cache hit for text")
            return self.cache.get(text)
        
        # Apply rate limiting
        if not self.config.is_within_rate_limit():
            raise RateLimitError("Rate limit exceeded")
        
        try:
            # Run OpenAI API call in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.logger.info("Making OpenAI API call...")
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4",  # Use latest GPT-4 for best Portuguese corrections
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.0  # Use deterministic output
                )
            )
            
            corrected = response.choices[0].message.content.strip()
            self.logger.info(f"Received response: {corrected}")
            
            # Cache the result
            self.cache.put(text, corrected)
            
            return corrected

        except OpenAIAPIError as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            if hasattr(e, 'status_code'):
                raise APIError(e.status_code, str(e))
            else:
                raise APIError(500, str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error in correct(): {str(e)}")
            self.logger.error(f"Error type: {type(e)}")
            raise SpellCheckError(f"Unexpected error: {str(e)}")

    @staticmethod
    def is_available() -> bool:
        """Check if spell checker is available."""
        return bool(os.getenv('OPENAI_API_KEY'))
