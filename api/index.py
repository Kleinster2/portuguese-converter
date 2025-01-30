from http.server import BaseHTTPRequestHandler

def handler(request):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": "Hello from Python!"
    }
