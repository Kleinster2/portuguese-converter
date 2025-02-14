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
        logger.error(f"Error in /convert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        text = data['text']
        
        # Get Azure credentials from environment variables
        speech_key = os.environ.get('AZURE_SPEECH_KEY')
        service_region = os.environ.get('AZURE_SPEECH_REGION')
        
        if not speech_key or not service_region:
            return jsonify({'error': 'Azure Speech Service credentials not configured'}), 500

        # Configure speech service
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"
        
        # Create SSML with prosody adjustments
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">
            <voice name="pt-BR-FranciscaNeural">
                <prosody rate="1.1" pitch="+0%">
                    {text}
                </prosody>
            </voice>
        </speak>
        """

        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            # Configure audio output to file
            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file.name)
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            
            # Synthesize speech
            result = speech_synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Read the temporary file
                with open(temp_file.name, 'rb') as audio_file:
                    audio_data = io.BytesIO(audio_file.read())
                
                # Clean up the temporary file
                os.unlink(temp_file.name)
                
                # Send the audio file
                return send_file(
                    audio_data,
                    mimetype='audio/wav',
                    as_attachment=True,
                    download_name='speech.wav'
                )
            else:
                error_details = f"Speech synthesis failed: {result.reason}"
                if result.cancellation_details:
                    error_details = f"{error_details}, {result.cancellation_details.reason}"
                logger.error(error_details)
                return jsonify({'error': error_details}), 500

    except Exception as e:
        logger.error(f"Error in /tts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run()
