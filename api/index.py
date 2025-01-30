from http.server import BaseHTTPRequestHandler
import json

def handler(request):
    """Handle incoming requests."""
    if request.method == "GET":
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Portuguese Converter API"
            })
        }
    else:
        return {
            "statusCode": 405,
            "body": json.dumps({
                "error": "Method not allowed"
            })
        }
