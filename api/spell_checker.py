from openai import OpenAI, OpenAIError
from cachetools import TTLCache
import logging
import traceback

logger = logging.getLogger(__name__)

class SpellCheckError(Exception):
    pass

class RateLimitError(SpellCheckError):
    pass

class APIError(SpellCheckError):
    pass

class SpellChecker:
    def __init__(self, config):
        if not config.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.cache = TTLCache(
            maxsize=config.cache_size,
            ttl=config.cache_ttl
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
        logger.info("SpellChecker initialized successfully")

    def correct_text(self, text):
        """Correct spelling in Portuguese text."""
        if not self.config.enabled:
            return text

        # Check cache first
        if text in self.cache:
            logger.info("Cache hit for text")
            return self.cache[text]

        # Check rate limit
        if not self.config.is_within_rate_limit():
            raise RateLimitError("Rate limit exceeded")

        try:
            # Make API call
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.0,
                timeout=30  # 30 second timeout
            )

            # Extract corrected text
            corrected_text = response.choices[0].message.content.strip()
            
            # Cache the result
            self.cache[text] = corrected_text
            
            return corrected_text

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            logger.error(traceback.format_exc())
            raise APIError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in spell checker: {str(e)}")
            logger.error(traceback.format_exc())
            raise SpellCheckError(f"Spell check failed: {str(e)}")
