from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import transform_tokens
import sys
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/convert', methods=['POST', 'OPTIONS'])
def convert():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text']
        if not isinstance(text, str):
            return jsonify({'error': 'Text must be a string'}), 400
            
        clean_tokens = text.split()
        transformed = transform_tokens(clean_tokens)
        result = ' '.join(transformed)
        
        return jsonify({'result': result})
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run()
