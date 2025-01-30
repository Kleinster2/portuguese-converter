from flask import Flask, request, jsonify
import os
import sys
import logging
import traceback
from flask_cors import CORS

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
CORS(app)  # Enable CORS for all routes

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

@app.route('/api/convert', methods=['POST', 'OPTIONS'])
def convert():
    # Handle preflight request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        logger.debug("Received POST request for conversion")
        if not request.is_json:
            logger.error("Request data is not JSON")
            return jsonify({
                'error': 'Invalid request format',
                'details': 'Request must be JSON'
            }), 400
            
        data = request.get_json()
        if data is None:
            logger.error("Failed to parse JSON data")
            return jsonify({
                'error': 'Invalid request format',
                'details': 'Invalid JSON data'
            }), 400
            
        logger.debug(f"Request data: {data}")
        text = data.get('text', '')
        if not text:
            logger.warning("No text provided in request")
            return jsonify({
                'error': 'Invalid request',
                'details': 'The request must include a "text" field'
            }), 400
        
        # First, try to spellcheck the text
        spellchecker = get_spellchecker()
        spell_explanation = None
        if spellchecker:
            try:
                text, spell_explanation = spellchecker.check_text(text)
                logger.debug(f"Spellcheck result: {spell_explanation}")
            except ValueError as e:
                logger.error(f"Error during spellcheck: {str(e)}")
                spell_explanation = f"Error during spellcheck: {str(e)}"
            except Exception as e:
                logger.error(f"Unexpected error during spellcheck: {str(e)}")
                traceback.print_exc()
                spell_explanation = f"Internal server error during spellcheck: {str(e)}"
        else:
            logger.warning("Spellchecker not initialized")
        
        # Then convert the text
        try:
            result = convert_text(text)
            logger.debug(f"Converted text result: {result}")
            
            if not isinstance(result, dict):
                logger.error(f"Invalid result type: {type(result)}")
                return jsonify({
                    'error': 'Conversion error',
                    'details': 'Invalid conversion result format'
                }), 500
            
            # Check for error in result
            if 'error' in result:
                logger.error(f"Error from convert_text: {result['error']}")
                return jsonify(result), 400
            
            # Validate required fields
            required_fields = {'before', 'after', 'explanations', 'combinations'}
            missing_fields = required_fields - set(result.keys())
            if missing_fields:
                logger.error(f"Missing fields in result: {missing_fields}")
                return jsonify({
                    'error': 'Conversion error',
                    'details': f'Missing required fields: {", ".join(missing_fields)}'
                }), 500
            
            # Build response
            response = {
                'before': result['before'],
                'after': result['after'],
                'explanations': result['explanations'],
                'combinations': result['combinations']
            }
            
            # Add spellcheck explanation if available
            if spell_explanation:
                response['spell_explanation'] = spell_explanation
            
            logger.debug(f"Sending response: {response}")
            return jsonify(response)
            
        except ValueError as e:
            logger.error(f"Value error during conversion: {str(e)}")
            return jsonify({
                'error': 'Conversion error',
                'details': str(e)
            }), 400
            
        except Exception as e:
            logger.error(f"Unexpected error during conversion: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'error': 'Internal server error',
                'details': str(e)
            }), 500
            
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
