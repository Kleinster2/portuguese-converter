from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
import json
import traceback
import serverless_wsgi

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

def create_success_response(data):
    """Create a standardized success response"""
    response = jsonify(data)
    response.headers.update({
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Accept, Origin',
        'Access-Control-Max-Age': '86400'
    })
    return response

def create_error_response(error_msg, details=None, status_code=500):
    """Create a standardized error response"""
    response = jsonify({
        'error': error_msg,
        'details': details or str(error_msg)
    })
    response.status_code = status_code
    response.headers.update({
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Accept, Origin',
        'Access-Control-Max-Age': '86400'
    })
    return response

@app.route('/api/convert', methods=['POST', 'OPTIONS'])
def convert():
    """Convert Portuguese text to show natural speech patterns."""
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Accept, Origin',
            'Access-Control-Max-Age': '86400'
        })
        return response

    try:
        # Get request data
        data = request.get_json()
        logger.debug(f"Received request data: {data}")
        
        if not data or 'text' not in data:
            return create_error_response('No text provided', status_code=400)
            
        text = data['text']
        if not isinstance(text, str):
            return create_error_response('Text must be a string', status_code=400)
            
        if not text.strip():
            return create_error_response('Text is empty', status_code=400)
            
        # Convert text
        result = convert_text(text)
        logger.debug(f"Conversion result: {result}")
        
        # Check for error in result
        if 'error' in result:
            return create_error_response(result['error'], result.get('details', ''), status_code=400)
        
        # Create response
        response_data = {
            'converted_text': result['after'],  # Frontend expects 'converted_text'
            'explanations': result.get('explanations', []),
            'before': result.get('before', text),
            'combinations': result.get('combinations', [])
        }
        logger.debug(f"Response data: {response_data}")
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in /api/convert: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response('Internal server error', str(e))

# Create handler for serverless function
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

# This is required for local development
if __name__ == '__main__':
    app.run(debug=True, port=3000)
