from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from portuguese_converter import convert_text_to_pt

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "message": "Portuguese Converter API is running. Send a POST request with 'text' field to convert."
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_json = json.loads(post_data.decode('utf-8'))
                text = request_json.get('text', '')
                
                if not text:
                    raise ValueError("No text provided")
                
                converted_text = convert_text_to_pt(text)
                response = {"converted_text": converted_text}
                status_code = 200
            else:
                raise ValueError("Empty request body")

        except json.JSONDecodeError:
            response = {"error": "Invalid JSON format"}
            status_code = 400
        except ValueError as e:
            response = {"error": str(e)}
            status_code = 400
        except Exception as e:
            response = {"error": "Internal server error"}
            status_code = 500
            print(f"Error: {str(e)}", file=sys.stderr)

        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
