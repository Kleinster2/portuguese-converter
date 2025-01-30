from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from portuguese_converter import convert_to_phonetic

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - return API info"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'message': 'Portuguese Converter API',
            'endpoints': {
                'GET /': 'API information',
                'POST /api/convert': 'Convert Portuguese text to phonetic'
            }
        }
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle POST requests - convert text"""
        try:
            # Read and parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            # Validate input
            if not data or 'text' not in data:
                self._send_error('Missing required field: text', 400)
                return
                
            text = data['text']
            if not isinstance(text, str):
                self._send_error('Text must be a string', 400)
                return
            
            # Convert text
            try:
                result = convert_to_phonetic(text)
                self._send_response({
                    'success': True,
                    'original': text,
                    'result': result
                })
            except Exception as e:
                self._send_error(f'Conversion error: {str(e)}', 500)
                
        except json.JSONDecodeError:
            self._send_error('Invalid JSON payload', 400)
        except Exception as e:
            self._send_error(f'Internal server error: {str(e)}', 500)

    def do_OPTIONS(self):
        """Handle OPTIONS requests - CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(''.encode())

    def _send_response(self, data, status=200):
        """Helper to send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, message, status):
        """Helper to send error response"""
        self._send_response({
            'success': False,
            'error': message
        }, status)
