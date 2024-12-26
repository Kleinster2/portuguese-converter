from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import transform_tokens
import sys
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "Portuguese Text Converter API is running!"

@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No data provided',
                'details': 'Request must include JSON data'
            }), 400
            
        if 'text' not in data:
            return jsonify({
                'error': 'No text provided',
                'details': 'Request must include "text" field'
            }), 400
            
        text = data['text']
        if not isinstance(text, str):
            return jsonify({
                'error': 'Invalid text format',
                'details': 'Text must be a string'
            }), 400
        
        if not text.strip():
            return jsonify({
                'error': 'Empty text',
                'details': 'Text cannot be empty'
            }), 400
        
        # Log input
        print(f"Input text: {text}", file=sys.stderr)
        
        # Split into tokens and transform
        tokens = text.split()
        print(f"Tokens: {tokens}", file=sys.stderr)
        
        transformed = transform_tokens(tokens)
        print(f"Transformed: {transformed}", file=sys.stderr)
        
        if not transformed:
            return jsonify({
                'error': 'Transformation failed',
                'details': 'No output was generated'
            }), 500
        
        result = ' '.join(transformed)
        print(f"Result: {result}", file=sys.stderr)
        
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
