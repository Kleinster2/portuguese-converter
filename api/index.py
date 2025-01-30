from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'API is working'})

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'status': 'ok'})
