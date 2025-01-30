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
        """Handle POST requests for text conversion"""
        # Read request body
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            
            # Validate input
            if 'text' not in data:
                self._send_error(400, 'Missing required field: text')
                return
                
            text = data['text']
            if not isinstance(text, str):
                self._send_error(400, 'Text must be a string')
                return
            
            # Convert the text
            try:
                result = convert_to_phonetic(text)
            except Exception as e:
                self._send_error(500, f'Conversion error: {str(e)}')
                return
            
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
            self._send_error(400, 'Invalid JSON payload')
        except Exception as e:
            self._send_error(500, f'Internal server error: {str(e)}')
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
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
