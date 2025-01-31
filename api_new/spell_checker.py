import logging
from openai import OpenAI
from cachetools import TTLCache
import time

logger = logging.getLogger(__name__)

class SpellCheckError(Exception):
    """Base class for spell check errors."""
    pass

class RateLimitError(SpellCheckError):
    """Raised when rate limit is exceeded."""
    pass

class APIError(SpellCheckError):
    """Raised when API request fails."""
    pass

class SpellChecker:
    def __init__(self, config):
        """Initialize spell checker with configuration."""
        try:
            self.config = config
            self.cache = TTLCache(
                maxsize=config.cache_size,
                ttl=config.cache_ttl
            )
            logger.info("Initializing OpenAI client...")
            self.client = OpenAI(
                api_key=config.api_key,
                timeout=30.0  # 30 second timeout
            )
            self.system_prompt = """
            You are a Portuguese text corrector. Your task is to:
            1. Fix spelling mistakes
            2. Add missing accents
            3. Correct grammar errors
            4. Maintain the original meaning
            5. Return ONLY the corrected text, nothing else
            
            Example:
            Input: "vc naum vai fazer isso hj?"
            Output: "você não vai fazer isso hoje?"
            """
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SpellChecker: {str(e)}")
            raise

    def correct_text(self, text):
        """Correct spelling in Portuguese text."""
        try:
            if not self.config.enabled:
                return text

            # Check cache first
            if text in self.cache:
                logger.info("Cache hit - returning cached result")
                return self.cache[text]

            logger.info("Cache miss - calling OpenAI API")
            
            # Check rate limit
            if not self.config.is_within_rate_limit():
                raise RateLimitError("Rate limit exceeded")

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.0,
                max_tokens=1000
            )

            # Extract corrected text
            corrected_text = response.choices[0].message.content.strip()
            
            # Cache the result
            self.cache[text] = corrected_text
            
            logger.info("Successfully corrected text")
            return corrected_text

        except Exception as e:
            logger.error(f"Error in correct_text: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            raise APIError(f"Failed to correct text: {str(e)}")
