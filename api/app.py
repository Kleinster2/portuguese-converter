from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import convert_text
from spell_checker import SpellChecker, SpellCheckError, RateLimitError, APIError
from config import SpellCheckConfig
import traceback
import logging
import asyncio
import concurrent.futures
import functools
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize thread pool for async operations
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# Initialize spell checker globally
try:
    config = SpellCheckConfig.from_env()
    spell_checker = SpellChecker(config)
    logger.info("Spell checker initialized successfully")
except Exception as e:
    logger.error(f"Error initializing spell checker: {str(e)}")
    logger.error(traceback.format_exc())
    spell_checker = None

def run_in_executor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        future = thread_pool.submit(func, *args, **kwargs)
        return future.result()
    return wrapper

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
                @run_in_executor
                def do_spell_check():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(spell_checker.correct_text(text))
                    finally:
                        loop.close()

                spell_checked_text = do_spell_check()
                logger.info("Spell check completed successfully")
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
