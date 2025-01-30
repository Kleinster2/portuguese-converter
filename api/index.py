import json
import os
import sys

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from portuguese_converter import convert_to_phonetic

def handle_request(request):
    """Process the request and return appropriate response"""
    method = request.get('method', '')
    
    # Common headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Handle OPTIONS (CORS preflight)
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    # Handle GET (API info)
    if method == 'GET':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Portuguese Converter API',
                'endpoints': {
                    'GET /': 'API information',
                    'POST /api/convert': 'Convert Portuguese text to phonetic'
                }
            })
        }

    # Handle POST (text conversion)
    if method == 'POST':
        try:
            # Parse request body
            body = json.loads(request.get('body', '{}'))
            
            # Validate input
            if not body or 'text' not in body:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'error': 'Missing required field: text'
                    })
                }
            
            text = body['text']
            if not isinstance(text, str):
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'error': 'Text must be a string'
                    })
                }
            
            # Convert text
            try:
                result = convert_to_phonetic(text)
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'original': text,
                        'result': result
                    })
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'error': f'Conversion error: {str(e)}'
                    })
                }
                
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid JSON payload'
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': f'Internal server error: {str(e)}'
                })
            }

    # Handle unsupported methods
    return {
        'statusCode': 405,
        'headers': headers,
        'body': json.dumps({
            'success': False,
            'error': 'Method not allowed'
        })
    }

def handler(request):
    """Main handler function"""
    try:
        return handle_request(request)
    except Exception as e:
        # Last resort error handling
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            })
        }
