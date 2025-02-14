from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from portuguese_converter import convert_text
import sys
import os
import io
import time
import traceback
import logging
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# Load environment variables
load_dotenv()

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
        return jsonify(result)
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug
        return jsonify({'error': str(e)}), 500

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text']
        
        # Load Azure credentials
        subscription_key = os.getenv('AZURE_SPEECH_KEY')
        region = os.getenv('AZURE_SPEECH_REGION')
        
        if not subscription_key or not region:
            return jsonify({'error': 'Azure credentials not configured'}), 500
        
        # Initialize speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key,
            region=region
        )
        
        # Set synthesis language and voice
        speech_config.speech_synthesis_language = "pt-BR"
        speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"
        
        # Create a unique temporary directory
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp', str(int(time.time() * 1000)))
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create a temporary file for the audio
        temp_filename = os.path.join(temp_dir, 'speech.wav')
        
        try:
            # Configure audio output to file
            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_filename)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # Generate SSML with prosody adjustments for better pronunciation
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">
                <voice name="pt-BR-FranciscaNeural">
                    <prosody rate="1.1" pitch="+0%">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            # Synthesize speech
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Read the audio file and send it as response
                with open(temp_filename, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                # Return audio file
                response = send_file(
                    io.BytesIO(audio_data),
                    mimetype='audio/wav',
                    as_attachment=True,
                    download_name='speech.wav'
                )
                
                return response
            else:
                error_details = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonErrorDetails)
                return jsonify({'error': f'Speech synthesis failed: {error_details}'}), 500
                
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up temporary files: {cleanup_error}")
                
    except Exception as e:
        logger.error(f"TTS Error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Vercel requires the app to be named 'app'
app.debug = True

if __name__ == '__main__':
    app.run(debug=True)
