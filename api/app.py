from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import convert_text
from spell_checker import SpellChecker, SpellCheckError, RateLimitError, APIError
from config import SpellCheckConfig
import sys
import os
import traceback
import logging
import asyncio
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Debug log environment variables
logger.info(f"OPENAI_API_KEY set: {bool(os.getenv('OPENAI_API_KEY'))}")
logger.info(f"SPELL_CHECK_ENABLED: {os.getenv('SPELL_CHECK_ENABLED')}")

# Ensure api directory is in Python path
api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.append(api_dir)
    logger.info(f"Added {api_dir} to Python path")

app = Flask(__name__)
CORS(app)

# Initialize configuration and spell checker
config = SpellCheckConfig.from_env()
spell_checker = None
if config.api_key:
    try:
        spell_checker = SpellChecker(config)
        logger.info("Spell checker initialized")
    except Exception as e:
        logger.error(f"Failed to initialize spell checker: {str(e)}")
else:
    logger.warning("Spell checker not available - OPENAI_API_KEY not set")

def async_route(f):
    """Decorator to handle async routes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "running", 
        "message": "Portuguese Text Converter API is running!",
        "spell_check_available": spell_checker is not None,
        "config": config.to_dict() if config else None
    })

@app.route('/api/config/spell_check', methods=['GET', 'POST'])
def spell_check_config():
    """Get or update spell check configuration."""
    global config, spell_checker
    
    if request.method == 'GET':
        return jsonify(config.to_dict())
    
    # POST request to update config
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No data provided',
                'details': 'Request must include JSON data'
            }), 400
        
        # Update config
        if 'enabled' in data:
            config.enabled = bool(data['enabled'])
        if 'rate_limit' in data:
            config.rate_limit = int(data['rate_limit'])
        if 'cache_size' in data:
            config.cache_size = int(data['cache_size'])
        if 'cache_ttl' in data:
            config.cache_ttl = int(data['cache_ttl'])
        
        # Reinitialize spell checker if needed
        if spell_checker:
            spell_checker = SpellChecker(config)
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'config': config.to_dict()
        })
        
    except (ValueError, TypeError) as e:
        return jsonify({
            'error': 'Invalid configuration value',
            'details': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error updating config: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(traceback.format_exc())
        
        # Get detailed error info
        error_details = str(e)
        if hasattr(e, '__dict__'):
            error_details = str(e.__dict__)
        
        return jsonify({
            'error': 'Server error',
            'details': error_details,
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/portuguese_converter', methods=['POST'])
@async_route
async def convert():
    try:
        # Get request data
        data = request.get_json()
        logger.info(f"Received request data: {data}")
        
        if not data:
            logger.error("No data provided in request")
            return jsonify({
                'error': 'No data provided',
                'details': 'Request must include JSON data'
            }), 400
            
        if 'text' not in data:
            logger.error("No text field in request data")
            return jsonify({
                'error': 'No text provided',
                'details': 'Request must include "text" field'
            }), 400
            
        text = data['text']
        logger.info(f"Processing text: {text}")
        
        if not isinstance(text, str):
            logger.error(f"Invalid text format: {type(text)}")
            return jsonify({
                'error': 'Invalid text format',
                'details': 'Text must be a string'
            }), 400

        # Check if spell checking is requested and available
        use_spell_check = data.get('use_spell_check', False)
        original_text = text
        spell_checked_text = None
        
        if use_spell_check:
            if spell_checker and config.enabled:
                try:
                    logger.info("Starting spell check...")
                    # Run spell check
                    spell_checked_text = await spell_checker.correct(text)
                    text = spell_checked_text  # Use corrected text for conversion
                    logger.info(f"Spell check completed: {spell_checked_text}")
                except RateLimitError as e:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'details': str(e),
                        'retry_after': 60  # Suggest retry after 60 seconds
                    }), 429
                except APIError as e:
                    return jsonify({
                        'error': 'OpenAI API error',
                        'details': str(e)
                    }), e.status
                except SpellCheckError as e:
                    return jsonify({
                        'error': 'Spell check error',
                        'details': str(e)
                    }), 500
            else:
                logger.warning("Spell check requested but not available or disabled")
                return jsonify({
                    'error': 'Spell check not available',
                    'details': 'OpenAI API key not configured or spell check disabled'
                }), 400

        # Convert text using existing pipeline
        result = convert_text(text)
        
        # Include original and spell-checked text in response
        response = {
            'original': original_text,
            'spell_checked': spell_checked_text,
            'converted': result['after'],  # Use 'after' instead of 'text'
            'explanations': result['explanations']
        }
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(traceback.format_exc())
        
        # Get detailed error info
        error_details = str(e)
        if hasattr(e, '__dict__'):
            error_details = str(e.__dict__)
        
        return jsonify({
            'error': 'Internal server error',
            'details': error_details,
            'traceback': traceback.format_exc()
        }), 500

@app.route('/convert', methods=['POST'])
def convert_new():
    try:
        data = request.get_json()
        text = data.get('text', '')
        print(f"Received text: {text}")  # Debug
        result = convert_text(text)
        print(f"Conversion result: {result}")  # Debug
        return jsonify({
            'original': result['original'],
            'before': result['before'],
            'after': result['after'],
            'explanations': result['explanations'],
            'combinations': result['combinations']
        })
        
    except Exception as e:
        print(f"Error in convert: {str(e)}")  # Debug
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Vercel requires the app to be named 'app'
app.debug = True

# Create a new route that matches Vercel's function pattern
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    if request.method == 'POST':
        return convert()
    return home()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
