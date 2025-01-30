from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    try:
        logger.info("Handling home route request")
        return jsonify({
            'message': 'Portuguese Text Converter API',
            'status': 'online'
        })
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/portuguese_converter', methods=['POST'])
def convert():
    try:
        logger.info("Handling convert request")
        data = request.get_json()
        if not data or 'text' not in data:
            logger.error("No text provided in request")
            return jsonify({'error': 'No text provided'}), 400

        text = data['text']
        logger.info(f"Received text: {text}")
        
        # Just echo back the text for now
        return jsonify({
            'original': text,
            'spell_checked': text,
            'converted': text,
            'explanations': []
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
