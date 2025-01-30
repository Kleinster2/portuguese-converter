from flask import Flask, request, jsonify, Response
import os
import sys
import logging
import traceback
from flask_cors import CORS
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)  # Insert at beginning to ensure our modules are found first
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

logger.debug(f"Python path: {sys.path}")
logger.debug(f"Current directory: {current_dir}")
logger.debug(f"Parent directory: {parent_dir}")

try:
    from portuguese_converter import convert_text
    from config import SpellCheckConfig
    from spellcheck import init_spellchecker, get_spellchecker
    logger.debug("Successfully imported local modules")
except ImportError as e:
    logger.error(f"Failed to import local modules: {e}")
    try:
        from api.portuguese_converter import convert_text
        from api.config import SpellCheckConfig
        from api.spellcheck import init_spellchecker, get_spellchecker
        logger.debug("Successfully imported modules with api prefix")
    except ImportError as e:
        logger.error(f"Failed to import modules with api prefix: {e}")
        raise

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})

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
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/', methods=['GET'])
def home():
    response = jsonify({'message': 'Portuguese Converter API is running'})
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/convert', methods=['POST', 'OPTIONS'])
def convert():
    # Handle preflight request
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
        response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
        return response

    try:
        logger.debug("Received POST request for conversion")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        # Get raw request data for debugging
        raw_data = request.get_data(as_text=True)
        logger.debug(f"Raw request data: {raw_data}")
        
        # Check content type
        content_type = request.headers.get('Content-Type', '')
        logger.debug(f"Content-Type: {content_type}")
        if not content_type.startswith('application/json'):
            logger.error(f"Invalid Content-Type: {content_type}")
            return create_error_response(
                'Invalid request format',
                'Content-Type must be application/json',
                400
            )
            
        if not request.is_json:
            logger.error("Request data is not JSON")
            return create_error_response(
                'Invalid request format',
                f'Request must be JSON. Raw data: {raw_data}',
                400
            )
            
        try:
            data = request.get_json()
            logger.debug(f"Parsed JSON data: {data}")
        except Exception as e:
            logger.error(f"Failed to parse JSON data: {str(e)}")
            logger.error(f"Raw data that failed to parse: {raw_data}")
            return create_error_response(
                'Invalid request format',
                f'Invalid JSON data: {str(e)}. Raw data: {raw_data}',
                400
            )
            
        if data is None:
            logger.error("JSON data is None")
            return create_error_response(
                'Invalid request format',
                f'Empty JSON data. Raw data: {raw_data}',
                400
            )
            
        logger.debug(f"Parsed request data: {data}")
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
                logger.error(traceback.format_exc())
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
                    f'Invalid conversion result format: {result}',
                    500
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
                    f'Missing required fields: {", ".join(missing_fields)}. Result: {result}',
                    500
                )
            
            # Build response
            response_data = {
                'before': result['before'],
                'after': result['after'],
                'explanations': result['explanations'],
                'combinations': result['combinations']
            }
            
            # Add spellcheck explanation if available
            if spell_explanation:
                response_data['spell_explanation'] = spell_explanation
            
            logger.debug(f"Sending response: {response_data}")
            response = jsonify(response_data)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        except ValueError as e:
            logger.error(f"Value error during conversion: {str(e)}")
            logger.error(traceback.format_exc())
            return create_error_response(
                'Conversion error',
                str(e),
                400
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during conversion: {str(e)}")
            logger.error(traceback.format_exc())
            return create_error_response(
                'Internal server error',
                str(e),
                500
            )
            
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(
            'Internal server error',
            str(e),
            500
        )

@app.after_request
def after_request(response):
    """Ensure CORS headers are set on all responses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
    return response

# Vercel requires a handler function
def handler(event, context):
    """Handle requests in Vercel serverless environment"""
    # Parse request data from event
    try:
        logger.debug(f"Received event: {event}")
        
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
        raw_headers = event.get('headers', {})
        # Normalize header names to lowercase for consistent access
        headers = {k.lower(): v for k, v in raw_headers.items()}
        body = event.get('body', '')
        
        logger.debug(f"Request headers: {headers}")
        logger.debug(f"Request body: {body}")
        
        # Parse JSON body if content-type is application/json
        content_type = headers.get('content-type', '')
        if method == 'POST' and ('application/json' in content_type.lower()):
            try:
                if isinstance(body, str):
                    body = json.loads(body)
                elif isinstance(body, bytes):
                    body = json.loads(body.decode('utf-8'))
                elif isinstance(body, dict):
                    # Already parsed by Vercel
                    pass
                else:
                    logger.error(f"Unexpected body type: {type(body)}")
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'error': 'Invalid request format',
                            'details': f'Unexpected body type: {type(body)}'
                        })
                    }
                    
                # Re-serialize to ensure valid JSON
                if not isinstance(body, dict):
                    body = json.loads(body)
                logger.debug(f"Parsed JSON body: {body}")
                
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.error(f"Failed to parse JSON body: {e}")
                logger.error(f"Raw body: {body}")
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Invalid request format',
                        'details': f'Invalid JSON data: {str(e)}'
                    })
                }
        
        # Create test request context
        with app.test_request_context(
            path=path,
            method=method,
            headers=headers,
            data=json.dumps(body) if isinstance(body, dict) else body,
            environ_base={'REMOTE_ADDR': event.get('ip', '')}
        ):
            try:
                # Dispatch request to Flask app
                response = app.full_dispatch_request()
                
                # Get response data
                response_data = response.get_data(as_text=True)
                logger.debug(f"Response data: {response_data}")
                
                # Convert Flask response to Vercel format
                return {
                    'statusCode': response.status_code,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        **dict(response.headers)
                    },
                    'body': response_data
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
        error_message = str(e)
        error_details = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"Error details: {error_details}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': error_message,
                'details': error_details
            })
        }

# This is required for local development
if __name__ == '__main__':
    app.run(debug=True)
