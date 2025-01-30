from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import convert_text
from spell_checker import SpellChecker, SpellCheckError, RateLimitError, APIError
from config import SpellCheckConfig
import traceback
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log Python environment info
logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Current working directory: {os.getcwd()}")

# Log environment variables (excluding sensitive values)
env_vars = {k: '***' if k in ['OPENAI_API_KEY'] else v for k, v in os.environ.items()}
logger.info(f"Environment variables: {env_vars}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize spell checker globally
try:
    logger.info("Initializing spell checker...")
    config = SpellCheckConfig.from_env()
    logger.info("Config loaded successfully")
    spell_checker = SpellChecker(config)
    logger.info("Spell checker initialized successfully")
except Exception as e:
    logger.error(f"Error initializing spell checker: {str(e)}")
    logger.error(f"Error type: {type(e)}")
    logger.error(traceback.format_exc())
    spell_checker = None

@app.route('/', methods=['GET'])
def home():
    try:
        logger.info("Handling home route request")
        return jsonify({
            'message': 'Portuguese Text Converter API',
            'endpoints': {
                '/': 'GET - This help message',
                '/api/portuguese_converter': 'POST - Convert Portuguese text'
            },
            'spell_checker_status': 'initialized' if spell_checker else 'not initialized'
        })
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/portuguese_converter', methods=['POST'])
def convert():
    try:
        logger.info("Handling convert request")
        data = request.get_json()
        if not data or 'text' not in data:
            logger.error("No text provided in request")
            return jsonify({'error': 'No text provided'}), 400

        text = data['text']
        use_spell_check = data.get('use_spell_check', True)
        
        logger.info(f"Processing text: {text}")
        logger.info(f"Spell check enabled: {use_spell_check}")
        
        # Store original text
        original_text = text
        spell_checked_text = text

        # Apply spell checking if enabled
        if use_spell_check and spell_checker:
            try:
                logger.info("Starting spell check")
                spell_checked_text = spell_checker.correct_text(text)
                logger.info("Spell check completed successfully")
            except Exception as e:
                logger.error(f"Spell check error: {str(e)}")
                logger.error(f"Error type: {type(e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    'error': 'Spell check failed',
                    'message': str(e),
                    'type': str(type(e))
                }), 500

        # Convert text using existing pipeline
        logger.info("Starting text conversion")
        result = convert_text(spell_checked_text)
        logger.info("Text conversion completed")
        
        # Include original and spell-checked text in response
        response = {
            'original': original_text,
            'spell_checked': spell_checked_text,
            'converted': result['after'],
            'explanations': result['explanations']
        }
        
        logger.info("Sending successful response")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'type': str(type(e)),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    try:
        logger.info(f"Catch-all route hit with path: {path}")
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
