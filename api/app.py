from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import transform_tokens, tokenize_punct, reattach_punct
import sys
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/convert', methods=['POST', 'OPTIONS'])
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
        
        print(f"Input text: {text}", file=sys.stderr)
        
        # First tokenize with punctuation
        token_pairs = tokenize_punct(text)
        print(f"Tokenized with punct: {token_pairs}", file=sys.stderr)
        
        # Get clean tokens for transformation
        clean_tokens = [token for token, _ in token_pairs]
        print(f"Clean tokens: {clean_tokens}", file=sys.stderr)
        
        # Transform the tokens
        transformed = transform_tokens(clean_tokens)
        print(f"Transformed tokens: {transformed}", file=sys.stderr)
        
        # Reattach punctuation
        if len(transformed) == len(token_pairs):
            result_pairs = [(t, p) for t, (_, p) in zip(transformed, token_pairs)]
            result = ' '.join(reattach_punct(result_pairs))
        else:
            # If token count changed, just join transformed tokens
            result = ' '.join(transformed)
            
        print(f"Final result: {result}", file=sys.stderr)
        
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
