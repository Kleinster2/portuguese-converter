import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# Load environment variables
load_dotenv()

def test_azure_connection():
    subscription_key = os.getenv('AZURE_SPEECH_KEY')
    region = os.getenv('AZURE_SPEECH_REGION')
    
    print(f"Testing Azure Speech Service connection...")
    print(f"Region: {region}")
    print(f"Key: {subscription_key[:5]}...{subscription_key[-5:]}")  # Only show part of the key for security
    
    try:
        # Initialize speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key,
            region=region
        )
        
        # Set synthesis language and voice
        speech_config.speech_synthesis_language = "pt-BR"
        speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"
        
        # Create synthesizer with null audio output (we don't need to hear anything)
        audio_config = speechsdk.audio.AudioOutputConfig(filename="test.wav")
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        # Try a simple synthesis
        print("\nTesting synthesis...")
        result = synthesizer.speak_text_async("Teste").get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Test successful! Azure Speech Service is working correctly.")
            return True
        else:
            if result.cancellation_details:
                print(f"Test failed with error: {result.cancellation_details.error_details}")
            else:
                print("Test failed with unknown error")
            return False
            
    except Exception as e:
        print(f"Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    test_azure_connection()
