from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import parse_qs, urlparse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - return API info"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'message': 'Portuguese Converter API is working',
            'endpoints': {
                'GET /': 'API information',
                'POST /api/convert': 'Convert Portuguese text to phonetic'
            }
        }
        self.wfile.write(json.dumps(response).encode())
    
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
                
            # TODO: Import and use actual converter
            # For now, return a simple response
            result = f"Converted: {text}"
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'success': True,
                'result': result
            }
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError:
            self._send_error(400, 'Invalid JSON payload')
        except Exception as e:
            self._send_error(500, f'Internal server error: {str(e)}')
    
    def _send_error(self, code, message):
        """Helper to send error responses"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'success': False,
            'error': message
        }
        self.wfile.write(json.dumps(response).encode())
