from flask import Flask, request, jsonify
import os
import sys
import logging
import traceback
from flask_cors import CORS
import json

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

def create_error_response(error_msg, details=None, status_code=500):
    """Create a standardized error response"""
    response = jsonify({
        'error': error_msg,
        'details': details or str(error_msg)
    })
    response.status_code = status_code
    return response

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
            return create_error_response(
                'Invalid request format',
                'Request must be JSON',
                400
            )
            
        try:
            data = request.get_json()
        except Exception as e:
            logger.error(f"Failed to parse JSON data: {str(e)}")
            return create_error_response(
                'Invalid request format',
                'Invalid JSON data',
                400
            )
            
        if data is None:
            logger.error("JSON data is None")
            return create_error_response(
                'Invalid request format',
                'Empty JSON data',
                400
            )
            
        logger.debug(f"Request data: {data}")
        text = data.get('text', '')
        if not text:
            logger.warning("No text provided in request")
            return create_error_response(
                'Invalid request',
                'The request must include a "text" field',
                400
            )
        
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
                return create_error_response(
                    'Conversion error',
                    'Invalid conversion result format'
                )
            
            # Check for error in result
            if 'error' in result:
                logger.error(f"Error from convert_text: {result['error']}")
                return create_error_response(
                    result['error'],
                    result.get('details', 'Unknown error'),
                    400
                )
            
            # Validate required fields
            required_fields = {'before', 'after', 'explanations', 'combinations'}
            missing_fields = required_fields - set(result.keys())
            if missing_fields:
                logger.error(f"Missing fields in result: {missing_fields}")
                return create_error_response(
                    'Conversion error',
                    f'Missing required fields: {", ".join(missing_fields)}'
                )
            
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
            return create_error_response(
                'Conversion error',
                str(e),
                400
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during conversion: {str(e)}")
            traceback.print_exc()
            return create_error_response(
                'Internal server error',
                str(e)
            )
            
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        traceback.print_exc()
        return create_error_response(
            'Internal server error',
            str(e)
        )

# Vercel requires a handler function
def handler(event, context):
    """Handle requests in Vercel serverless environment"""
    # Parse request data from event
    try:
        path = event.get('path', '/')
        if not path.startswith('/'):
            path = '/' + path
            
        # Get request method
        method = event.get('method', 'GET')
        if method == 'OPTIONS':
            # Handle CORS preflight
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Accept',
                'Access-Control-Max-Age': '86400',  # 24 hours
            }
            return {
                'statusCode': 204,
                'headers': headers,
                'body': ''
            }
            
        # Get headers and body
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Create test request context
        with app.test_request_context(
            path=path,
            method=method,
            headers=headers,
            data=body,
            environ_base={'REMOTE_ADDR': event.get('ip', '')}
        ):
            try:
                # Dispatch request to Flask app
                response = app.full_dispatch_request()
                
                # Convert Flask response to Vercel format
                return {
                    'statusCode': response.status_code,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        **dict(response.headers)
                    },
                    'body': response.get_data(as_text=True)
                }
                
            except Exception as e:
                logger.error(f"Error in request dispatch: {str(e)}")
                traceback.print_exc()
                error_response = create_error_response('Internal server error', str(e))
                return {
                    'statusCode': error_response.status_code,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        **dict(error_response.headers)
                    },
                    'body': error_response.get_data(as_text=True)
                }
                
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}")
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }

if __name__ == '__main__':
    app.run(debug=True)
