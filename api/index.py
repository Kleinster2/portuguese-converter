from http.server import BaseHTTPRequestHandler
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
import json

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
    logger.error(str(e))

# Initialize Flask app
app = Flask(__name__)
CORS(app)

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', f'{content_type}; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_json_response(self, data, status_code=200):
        try:
            self._set_headers(status_code)
            response = json.dumps(data, ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")
            self._set_headers(500)
            error_response = json.dumps({'error': 'Internal server error'}, ensure_ascii=False)
            self.wfile.write(error_response.encode('utf-8'))

    def do_GET(self):
        if self.path == '/api/test':
            self._send_json_response({"message": "API is working!"})
        else:
            self._set_headers(404)
            
    def do_POST(self):
        if self.path == '/api/convert':
            content_length = int(self.headers.get('Content-Length', 0))
            try:
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                if not data or 'text' not in data:
                    self._send_json_response({'error': 'No text provided'}, 400)
                    return
                    
                text = data['text']
                if not isinstance(text, str):
                    self._send_json_response({'error': 'Text must be a string'}, 400)
                    return
                    
                if not text.strip():
                    self._send_json_response({'error': 'Text is empty'}, 400)
                    return
                
                logger.debug(f"Input text: {text}")
                result = convert_text(text)
                logger.debug(f"Conversion result: {result}")
                
                if 'error' in result:
                    self._send_json_response({'error': result['error']}, 400)
                    return
                
                response = {
                    'converted_text': result['after'],
                    'explanations': result.get('explanations', []),
                    'before': result.get('before', text),
                    'combinations': result.get('combinations', [])
                }
                logger.debug(f"Response data: {response}")
                self._send_json_response(response)
                
            except UnicodeDecodeError as e:
                logger.error(f"Unicode decode error: {str(e)}")
                self._send_json_response({'error': 'Invalid UTF-8 encoding'}, 400)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                self._send_json_response({'error': 'Invalid JSON'}, 400)
            except Exception as e:
                logger.error(f"Error in /api/convert: {str(e)}")
                self._send_json_response({'error': str(e)}, 500)
        else:
            self._set_headers(404)

    def do_OPTIONS(self):
        self._set_headers()
