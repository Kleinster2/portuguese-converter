from http.server import BaseHTTPRequestHandler
from json import dumps

def handler(request, response):
    return {
        'statusCode': 200,
        'body': dumps({'message': 'Hello from Python!'})
    }
