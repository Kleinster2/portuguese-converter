from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import portuguese_converter module
try:
    from portuguese_converter import convert_text
    logger.debug("Successfully imported portuguese_converter module")
except ImportError as e:
    logger.error(f"Failed to import portuguese_converter: {e}")
    logger.error(traceback.format_exc())

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({"message": "API is working!"})

@app.route('/api/convert', methods=['POST'])
def convert():
    """Convert Portuguese text to show natural speech patterns."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text']
        if not isinstance(text, str):
            return jsonify({'error': 'Text must be a string'}), 400
            
        if not text.strip():
            return jsonify({'error': 'Text is empty'}), 400
            
        result = convert_text(text)
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'converted_text': result['after'],
            'explanations': result.get('explanations', []),
            'before': result.get('before', text),
            'combinations': result.get('combinations', [])
        })
        
    except Exception as e:
        logger.error(f"Error in /api/convert: {str(e)}")
        return jsonify({'error': str(e)}), 500

def handler(event, context):
    """Vercel handler function"""
    return app
