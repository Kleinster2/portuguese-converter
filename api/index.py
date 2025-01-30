from flask import Flask, request, jsonify
import os
import sys
import logging
import traceback

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from api.portuguese_converter import convert_text
from api.config import SpellCheckConfig
from api.spellcheck import init_spellchecker, get_spellchecker

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize spellchecker
try:
    config = SpellCheckConfig.from_env()
    init_spellchecker(config)
    logger.info("Spellchecker initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize spellchecker: {str(e)}\n{traceback.format_exc()}")

@app.route('/api/', methods=['GET'])
def home():
    return jsonify({'message': 'Portuguese Converter API is running'})

@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        logger.debug("Received POST request for conversion")
        data = request.get_json()
        logger.debug(f"Request data: {data}")
        text = data.get('text', '')
        if not text:
            logger.warning("No text provided in request")
            return jsonify({'error': 'No text provided'}), 400
        
        # First, try to spellcheck the text
        spellchecker = get_spellchecker()
        if spellchecker:
            try:
                text, spell_explanation = spellchecker.check_text(text)
                logger.debug(f"Spellcheck result: {spell_explanation}")
            except Exception as e:
                logger.error(f"Spellcheck error: {str(e)}\n{traceback.format_exc()}")
                spell_explanation = f"Error during spellcheck: {str(e)}"
        else:
            logger.warning("Spellchecker not initialized")
            spell_explanation = None
        
        # Then convert the text
        result = convert_text(text)
        logger.debug(f"Converted text result: {result}")
        
        if isinstance(result, dict):
            response = {
                'before': result.get('before', text),
                'after': result.get('after', text),
                'explanations': result.get('explanations', []),
                'combinations': result.get('combinations', [])
            }
            # Add spellcheck explanation if available
            if spell_explanation:
                response['spell_corrections'] = spell_explanation
            return jsonify(response)
        else:
            # Fallback for string result
            response = {
                'before': text,
                'after': result
            }
            if spell_explanation:
                response['spell_corrections'] = spell_explanation
            return jsonify(response)
            
    except Exception as e:
        error_msg = f"Error during conversion: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500
