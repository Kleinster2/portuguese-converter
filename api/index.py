from flask import Flask, request, jsonify
import os
import sys
import logging

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from portuguese_converter import convert_text
from config import SpellCheckConfig
from spellcheck import init_spellchecker, get_spellchecker

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Initialize spellchecker
config = SpellCheckConfig.from_env()
init_spellchecker(config)

@app.route('/api/', methods=['GET'])
def home():
    return jsonify({'message': 'Portuguese Converter API is running'})

@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        logging.debug("Received POST request for conversion")
        data = request.get_json()
        logging.debug(f"Request data: {data}")
        text = data.get('text', '')
        if not text:
            logging.warning("No text provided in request")
            return jsonify({'error': 'No text provided'}), 400
        
        # First, try to spellcheck the text
        spellchecker = get_spellchecker()
        if spellchecker:
            text, spell_explanation = spellchecker.check_text(text)
        else:
            spell_explanation = None
        
        # Then convert the text
        result = convert_text(text)
        logging.debug(f"Converted text result: {result}")
        
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
        logging.error(f"Error during conversion: {str(e)}")
        return jsonify({'error': str(e)}), 500
