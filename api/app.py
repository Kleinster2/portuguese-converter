from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import transform_tokens
import sys
import os
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure api directory is in Python path
api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.append(api_dir)
    logger.info(f"Added {api_dir} to Python path")

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "running", "message": "Portuguese Text Converter API is running!"})

@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        # Get request data
        data = request.get_json()
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
        if not isinstance(text, str):
            logger.error(f"Invalid text format: {type(text)}")
            return jsonify({
                'error': 'Invalid text format',
                'details': 'Text must be a string'
            }), 400
        
        if not text.strip():
            logger.error("Empty text provided")
            return jsonify({
                'error': 'Empty text',
                'details': 'Text cannot be empty'
            }), 400
        
        # Log input
        logger.info(f"Processing text: {text}")
        
        # Split into tokens and transform
        tokens = text.split()
        logger.info(f"Tokens: {tokens}")
        
        transformed = transform_tokens(tokens)
        logger.info(f"Transformed tokens: {transformed}")
        
        if not transformed:
            logger.error("Transformation returned no results")
            return jsonify({
                'error': 'Transformation failed',
                'details': 'No output was generated'
            }), 500
        
        result = ' '.join(transformed)
        logger.info(f"Final result: {result}")
        
        return jsonify({'result': result})
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

# Vercel requires the app to be named 'app'
app.debug = True

if __name__ == '__main__':
    # Only run the development server if we're running locally
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
