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
    def do_GET(self):
        if self.path == '/api/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"message": "API is working!"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        if self.path == '/api/convert':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                if not data or 'text' not in data:
                    self.send_error(400, 'No text provided')
                    return
                    
                text = data['text']
                if not isinstance(text, str):
                    self.send_error(400, 'Text must be a string')
                    return
                    
                if not text.strip():
                    self.send_error(400, 'Text is empty')
                    return
                    
                result = convert_text(text)
                if 'error' in result:
                    self.send_error(400, result['error'])
                    return
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'converted_text': result['after'],
                    'explanations': result.get('explanations', []),
                    'before': result.get('before', text),
                    'combinations': result.get('combinations', [])
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                logger.error(f"Error in /api/convert: {str(e)}")
                self.send_error(500, str(e))
        else:
            self.send_response(404)
            self.end_headers()
