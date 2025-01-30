from flask import Flask, request, Response, jsonify
import json
import os
import sys

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from portuguese_converter import convert_to_phonetic

app = Flask(__name__)

def create_response(data, status_code=200):
    """Helper to create consistent JSON responses"""
    return Response(
        json.dumps(data),
        status=status_code,
        mimetype='application/json',
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    )

@app.route('/', methods=['GET'])
def home():
    """API information endpoint"""
    return create_response({
        'message': 'Portuguese Converter API',
        'endpoints': {
            'GET /': 'API information',
            'POST /api/convert': 'Convert Portuguese text to phonetic'
        }
    })

@app.route('/api/convert', methods=['POST'])
def convert():
    """Convert Portuguese text to phonetic"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'text' not in data:
            return create_response({
                'success': False,
                'error': 'Missing required field: text'
            }, 400)
        
        text = data['text']
        if not isinstance(text, str):
            return create_response({
                'success': False,
                'error': 'Text must be a string'
            }, 400)
        
        # Convert the text
        try:
            result = convert_to_phonetic(text)
            return create_response({
                'success': True,
                'original': text,
                'result': result
            })
        except Exception as e:
            return create_response({
                'success': False,
                'error': f'Conversion error: {str(e)}'
            }, 500)
            
    except Exception as e:
        return create_response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, 500)

@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    """Handle CORS preflight requests"""
    return create_response({})

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return create_response({
        'success': False,
        'error': 'Not found'
    }, 404)

@app.errorhandler(405)
def method_not_allowed(e):
    return create_response({
        'success': False,
        'error': 'Method not allowed'
    }, 405)
