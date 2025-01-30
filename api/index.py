from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import parse_qs, urlparse
import sys
import logging

# Add the api directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from portuguese_converter import convert_to_phonetic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - return API info"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            'message': 'Portuguese Converter API is working',
            'endpoints': {
                'GET /': 'API information',
                'POST /api/convert': 'Convert Portuguese text to phonetic'
            }
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for text conversion"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            # Validate input
            if 'text' not in data:
                self._send_error(400, 'Missing required field: text')
                return
                
            text = data['text']
            if not isinstance(text, str):
                self._send_error(400, 'Text must be a string')
                return
            
            logger.info(f"Converting text: {text}")
            
            # Convert the text using our converter
            try:
                result = convert_to_phonetic(text)
                logger.info(f"Conversion result: {result}")
            except Exception as e:
                logger.error(f"Conversion error: {str(e)}")
                self._send_error(500, f'Conversion error: {str(e)}')
                return
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'success': True,
                'original': text,
                'result': result
            }
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
            self._send_error(400, 'Invalid JSON payload')
        except Exception as e:
            logger.error(f"Internal server error: {str(e)}")
            self._send_error(500, f'Internal server error: {str(e)}')
    
    def _send_error(self, code, message):
        """Helper to send error responses"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            'success': False,
            'error': message
        }
        self.wfile.write(json.dumps(response).encode())
