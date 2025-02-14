from api.tts_converter import TTSConverter
import os

def test_colloquial():
    # Initialize converter
    converter = TTSConverter()
    
    # Test phrase with colloquial transformations
    text = "Não sei, mas o trabalho está muito difícil."  # Testing: não→num, trabalho→trabaiu, muito→muitu
    output_file = "colloquial_test.wav"
    
    # Clean up previous file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    
    print(f"Original text: {text}")
    
    # Generate speech with phonetic transformations
    result = converter.synthesize_speech_with_phonemes(text, output_file)
    
    if result and os.path.exists(output_file):
        print("Audio generated successfully!")
        # Play the audio
        os.system(f'start powershell -Command "Start-Process {output_file}"')
    else:
        print("Failed to generate audio")

if __name__ == "__main__":
    test_colloquial()
