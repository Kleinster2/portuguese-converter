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

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def catch_all(path):
    """Handle all routes"""
    logger.debug(f"Received request for path: {path}")
    logger.debug(f"Method: {request.method}")
    logger.debug(f"Headers: {dict(request.headers)}")
    
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
        response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
        return response
        
    # Handle root path
    if not path:
        response = jsonify({'status': 'ok', 'message': 'Portuguese Converter API is running'})
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    # Handle /api/convert
    if path == 'api/convert' and request.method == 'POST':
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
            
    # Handle unknown paths
    return create_error_response('Not found', f'Path not found: {path}', 404)

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
    logger.debug(f"Received Vercel event: {event}")
    
    try:
        # Get the HTTP method
        method = event.get('method', 'GET')
        
        # Get the path
        path = event.get('path', '/')
        if not path.startswith('/'):
            path = '/' + path
            
        # Get headers
        headers = event.get('headers', {})
        
        # Get body if present
        body = event.get('body', '')
        if isinstance(body, str) and body:
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                pass
        
        # Create test request context
        with app.test_request_context(
            path=path,
            method=method,
            headers=headers,
            json=body if isinstance(body, dict) else None,
            data=body if not isinstance(body, dict) else None,
            environ_base={'REMOTE_ADDR': event.get('ip', '')}
        ):
            try:
                # Dispatch request to Flask app
                response = app.full_dispatch_request()
                
                # Convert Flask response to Vercel format
                return {
                    'statusCode': response.status_code,
                    'headers': dict(response.headers),
                    'body': response.get_data(as_text=True)
                }
                
            except Exception as e:
                logger.error(f"Error in request dispatch: {str(e)}")
                logger.error(traceback.format_exc())
                error_response = create_error_response('Internal server error', str(e))
                return {
                    'statusCode': error_response.status_code,
                    'headers': dict(error_response.headers),
                    'body': error_response.get_data(as_text=True)
                }
                
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'details': ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            })
        }

# This is required for local development
if __name__ == '__main__':
    app.run(debug=True)
