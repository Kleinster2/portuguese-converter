from api.tts_converter import TTSConverter
import os

def quick_test():
    # Initialize converter
    converter = TTSConverter()
    
    # Test phrase
    text = "Olá, tudo bem?"
    output_file = "quick_test.wav"
    
    # Clean up previous file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Generate speech
    print(f"Converting text: {text}")
    result = converter.synthesize_speech(text, output_file)
    
    if result and os.path.exists(output_file):
        print(f"Audio generated successfully: {output_file}")
        # Play the audio
        os.system(f'start powershell -Command "Start-Process {output_file}"')
    else:
        print("Failed to generate audio")

if __name__ == "__main__":
    quick_test()
