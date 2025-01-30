from openai import OpenAI
import logging
from typing import Dict, Optional, Tuple
from api.config import SpellCheckConfig
from api.cache import TTLCache

logger = logging.getLogger(__name__)

class SpellChecker:
    def __init__(self, config: SpellCheckConfig):
        self.config = config
        self.cache = TTLCache(max_size=config.cache_size, ttl=config.cache_ttl)
        self.client = OpenAI(api_key=config.api_key)

    def check_text(self, text: str) -> Tuple[str, Optional[str]]:
        """
        Check and correct Portuguese text using GPT-4.
        Returns tuple of (corrected_text, explanation) or (original_text, error_message) if error.
        """
        if not self.config.enabled:
            logger.info("Spellcheck is disabled")
            return text, None

        # Check cache first
        cached_result = self.cache.get(text)
        if cached_result:
            logger.info("Using cached spellcheck result")
            return cached_result

        if not self.config.is_within_rate_limit():
            logger.warning("Rate limit exceeded for spellcheck")
            return text, "Rate limit exceeded. Please try again later."

        try:
            # Craft a prompt that asks GPT-4 to focus on Portuguese spelling/grammar
            messages = [
                {"role": "system", "content": (
                    "You are a Portuguese language expert. Your task is to:"
                    "\n1. Check for spelling and grammar errors"
                    "\n2. Preserve informal/slang style if present"
                    "\n3. Only make corrections for clear errors"
                    "\n4. Explain any corrections made"
                    "\nRespond in JSON format with 'corrected' and 'explanation' fields."
                )},
                {"role": "user", "content": f"Check this Portuguese text: {text}"}
            ]

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.1,  # Low temperature for more consistent corrections
                max_tokens=200,
                response_format={ "type": "json_object" }
            )

            result = response.choices[0].message.content
            data = eval(result)  # Safe since we requested JSON from GPT-4
            
            corrected = data.get('corrected', text)
            explanation = data.get('explanation', None)

            # Cache the result
            self.cache.put(text, (corrected, explanation))

            return corrected, explanation

        except Exception as e:
            logger.error(f"Error in spellcheck: {str(e)}")
            return text, f"Error during spellcheck: {str(e)}"

# Global instance
_instance: Optional[SpellChecker] = None

def init_spellchecker(config: SpellCheckConfig):
    """Initialize the global spellchecker instance."""
    global _instance
    _instance = SpellChecker(config)

def get_spellchecker() -> Optional[SpellChecker]:
    """Get the global spellchecker instance."""
    return _instance
