from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from portuguese_converter import convert_text
import sys
import os
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure api directory is in Python path
api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.append(api_dir)
    logger.info(f"Added {api_dir} to Python path")

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('..', 'index.html')

@app.route('/api/portuguese_converter', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text']
        result = convert_text(text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/convert', methods=['POST'])
def convert_new():
    try:
        data = request.get_json()
        text = data.get('text', '')
        print(f"Received text: {text}")  # Debug
        result = convert_text(text)
        print(f"Conversion result: {result}")  # Debug
        return jsonify({
            'original': result['original'],
            'before': result['before'],
            'after': result['after'],
            'explanations': result['explanations'],
            'combinations': result['combinations']
        })
        
    except Exception as e:
        print(f"Error in convert: {str(e)}")  # Debug
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Vercel requires the app to be named 'app'
app.debug = True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
