from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import convert_text
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

@app.route('/api/portuguese_converter', methods=['POST'])
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
        
        # Convert the text
        try:
            result = convert_text(text)
            logger.info(f"Successfully converted text: {text[:50]}...")
            
            # Return in the format expected by frontend
            if isinstance(result, dict) and 'before' in result and 'after' in result:
                return jsonify(result)
            else:
                logger.error(f"Unexpected result format from convert_text: {result}")
                return jsonify({
                    'error': 'Invalid result format',
                    'details': 'Internal server error'
                }), 500
        except Exception as e:
            logger.error(f"Error in convert_text: {str(e)}")
            traceback.print_exc()
            return jsonify({
                'error': 'Conversion error',
                'details': str(e)
            }), 500

    except Exception as e:
        logger.error(f"Error converting text: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Server error',
            'details': str(e)
        }), 500

@app.route('/convert', methods=['POST'])
def convert_new():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        result = convert_text(text)
        
        return jsonify({
            'original': result['original'],
            'before': result['before'],
            'after': result['after'],
            'explanations': result['explanations'],
            'combinations': result['combinations']
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Vercel requires the app to be named 'app'
app.debug = True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
