from flask import Flask, Response
import json

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    response = {
        'message': 'Hello from Flask!'
    }
    return Response(
        json.dumps(response),
        mimetype='application/json',
        headers={
            'Access-Control-Allow-Origin': '*'
        }
    )
