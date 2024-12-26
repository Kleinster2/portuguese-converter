from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import transform_tokens

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['POST'])
def convert():
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
        print(f"Error: {str(e)}")  # Log the error
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run()
