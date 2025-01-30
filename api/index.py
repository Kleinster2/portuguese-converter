from flask import Flask, request, jsonify
import os
import sys
import logging

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from portuguese_converter import convert_text

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/api/', methods=['GET'])
def home():
    return jsonify({'message': 'Portuguese Converter API is running'})

@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        logging.debug("Received POST request for conversion")
        data = request.get_json()
        logging.debug(f"Request data: {data}")
        text = data.get('text', '')
        if not text:
            logging.warning("No text provided in request")
            return jsonify({'error': 'No text provided'}), 400
        converted_text = convert_text(text)
        logging.debug(f"Converted text: {converted_text}")
        return jsonify({
            'before': text,
            'after': converted_text
        })
    except Exception as e:
        logging.error(f"Error during conversion: {str(e)}")
        return jsonify({'error': str(e)}), 500
