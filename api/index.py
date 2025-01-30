from flask import Flask, request, jsonify
import os
import sys

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from portuguese_converter import convert_text_to_pt

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Portuguese Converter API is running'})

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        converted_text = convert_text_to_pt(text)
        return jsonify({'converted_text': converted_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
