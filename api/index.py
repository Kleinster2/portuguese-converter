from http.server import BaseHTTPRequestHandler
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import logging
import json
import io
import azure.cognitiveservices.speech as speechsdk
import tempfile

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import portuguese_converter module
try:
    from portuguese_converter import convert_text
    logger.debug("Successfully imported portuguese_converter module")
except ImportError as e:
    logger.error(f"Failed to import portuguese_converter: {e}")
    logger.error(str(e))

# Initialize Flask app
app = Flask(__name__)
CORS(app)

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', f'{content_type}; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_json_response(self, data, status_code=200):
        try:
            self._set_headers(status_code)
            response = json.dumps(data, ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")
            self._set_headers(500)
            error_response = json.dumps({'error': 'Internal server error'}, ensure_ascii=False)
            self.wfile.write(error_response.encode('utf-8'))

    def do_GET(self):
        if self.path == '/api/test':
            self._send_json_response({"message": "API is working!"})
        else:
            self._set_headers(404)
            
    def do_POST(self):
        if self.path == '/api/convert':
            content_length = int(self.headers.get('Content-Length', 0))
            try:
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                if not data or 'text' not in data:
                    self._send_json_response({'error': 'No text provided'}, 400)
                    return
                    
                text = data['text']
                if not isinstance(text, str):
                    self._send_json_response({'error': 'Text must be a string'}, 400)
                    return
                    
                if not text.strip():
                    self._send_json_response({'error': 'Text is empty'}, 400)
                    return
                
                logger.debug(f"Input text: {text}")
                result = convert_text(text)
                logger.debug(f"Conversion result: {result}")
                
                if 'error' in result:
                    self._send_json_response({'error': result['error']}, 400)
                    return
                
                response = {
                    'converted_text': result['after'],
                    'explanations': result.get('explanations', []),
                    'before': result.get('before', text),
                    'combinations': result.get('combinations', [])
                }
                logger.debug(f"Response data: {response}")
                self._send_json_response(response)
                
            except UnicodeDecodeError as e:
                logger.error(f"Unicode decode error: {str(e)}")
                self._send_json_response({'error': 'Invalid UTF-8 encoding'}, 400)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                self._send_json_response({'error': 'Invalid JSON'}, 400)
            except Exception as e:
                logger.error(f"Error in /api/convert: {str(e)}")
                self._send_json_response({'error': str(e)}, 500)
        else:
            self._set_headers(404)

    def do_OPTIONS(self):
        self._set_headers()

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
        logger.error(f"Error in /api/portuguese_converter: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert', methods=['POST'])
def convert_new():
    try:
        data = request.get_json()
        text = data.get('text', '')
        result = convert_text(text)
        
        return jsonify({
            'text': result.get('original', text),
            'converted_text': result.get('after', ''),
            'before': result.get('before', ''),
            'after': result.get('after', ''),
            'explanations': result.get('explanations', []),
            'combinations': result.get('combinations', [])
        })
        
    except Exception as e:
        logger.error(f"Error in /api/convert: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            logger.error("No text provided in TTS request")
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text']
        logger.debug(f"TTS request for text: {text}")
        
        # Check Azure credentials
        speech_key = os.getenv('AZURE_SPEECH_KEY')
        speech_region = os.getenv('AZURE_SPEECH_REGION')
        
        if not speech_key or not speech_region:
            logger.error("Azure credentials not found")
            return jsonify({'error': 'Azure credentials not configured'}), 500
        
        # Configure speech service
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region
        )
        
        logger.debug("Speech config created successfully")
        
        # Set synthesis language and voice
        speech_config.speech_synthesis_language = "pt-BR"
        speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"
        
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file.name)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # Generate speech
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Read the audio file
                with open(temp_file.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                # Clean up
                os.unlink(temp_file.name)
                
                # Return the audio file
                return send_file(
                    io.BytesIO(audio_data),
                    mimetype='audio/wav',
                    as_attachment=True,
                    download_name='speech.wav'
                )
            else:
                return jsonify({'error': 'Failed to generate speech'}), 500
                
    except Exception as e:
        logger.error(f"Error in TTS: {str(e)}")
        return jsonify({'error': str(e)}), 500
