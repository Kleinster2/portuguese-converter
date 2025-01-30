from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import convert_text
from spell_checker import SpellChecker, SpellCheckError, RateLimitError, APIError
from config import SpellCheckConfig
import traceback
import logging
import asyncio
import functools
import concurrent.futures
import os
import sys

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize spell checker globally
try:
    config = SpellCheckConfig.from_env()
    spell_checker = SpellChecker(config)
    logger.info("Spell checker initialized successfully")
except Exception as e:
    logger.error(f"Error initializing spell checker: {str(e)}")
    logger.error(traceback.format_exc())
    spell_checker = None

# Debug log environment variables
logger.info(f"OPENAI_API_KEY set: {bool(os.getenv('OPENAI_API_KEY'))}")
logger.info(f"SPELL_CHECK_ENABLED: {os.getenv('SPELL_CHECK_ENABLED')}")

# Ensure api directory is in Python path
api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.append(api_dir)
    logger.info(f"Added {api_dir} to Python path")

def async_timeout(timeout):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Operation timed out after {timeout} seconds")
        return wrapper
    return decorator

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

def run_async(func):
    loop = get_or_create_eventloop()
    return loop.run_until_complete(func)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Portuguese Text Converter API',
        'endpoints': {
            '/': 'GET - This help message',
            '/api/portuguese_converter': 'POST - Convert Portuguese text'
        }
    })

@app.route('/api/portuguese_converter', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        text = data['text']
        use_spell_check = data.get('use_spell_check', True)
        
        # Store original text
        original_text = text
        spell_checked_text = text

        # Apply spell checking if enabled
        if use_spell_check and spell_checker:
            try:
                @async_timeout(10)  # 10 second timeout
                async def spell_check():
                    return await spell_checker.correct(text)
                
                spell_checked_text = run_async(spell_check())
                logger.info("Spell check completed successfully")
            except TimeoutError:
                logger.error("Spell check timed out")
                return jsonify({
                    'error': 'Spell check timed out',
                    'message': 'The spell checker took too long to respond'
                }), 504
            except Exception as e:
                logger.error(f"Spell check error: {str(e)}")
                return jsonify({
                    'error': 'Spell check failed',
                    'message': str(e)
                }), 500

        # Convert text using existing pipeline
        result = convert_text(spell_checked_text)
        
        # Include original and spell-checked text in response
        response = {
            'original': original_text,
            'spell_checked': spell_checked_text,
            'converted': result['after'],
            'explanations': result['explanations']
        }
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    try:
        if request.method == 'POST':
            return convert()
        return home()
    except Exception as e:
        logger.error(f"Error in catch_all: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
