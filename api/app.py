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
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text']
        if not isinstance(text, str):
            return jsonify({'error': 'Text must be a string'}), 400
        
        print(f"Input text: {text}", file=sys.stderr)
        
        # Split into tokens and transform
        tokens = text.split()
        print(f"Tokens: {tokens}", file=sys.stderr)
        
        transformed = transform_tokens(tokens)
        print(f"Transformed: {transformed}", file=sys.stderr)
        
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
