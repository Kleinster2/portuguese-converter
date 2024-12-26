from flask import Flask, request, jsonify
from flask_cors import CORS
from portuguese_converter import transform_tokens

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
        
    text = data['text']
    clean_tokens = text.split()
    transformed = transform_tokens(clean_tokens)
    result = ' '.join(transformed)
    
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run()
