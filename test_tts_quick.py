from dotenv import load_dotenv
import os
from api.tts_converter import TTSConverter
from api.portuguese_converter import transform_text

def test_speak():
    # Load environment variables
    load_dotenv()
    
    # Initialize TTS
    tts = TTSConverter()
    
    # Test text
    text = "Olá, tudo bem? Não trabalho hoje porque estou muito cansado."
    print(f"Original text: {text}")
    
    # Transform to colloquial form
    result = transform_text(text)
    transformed = result['after']
    print(f"Transformed text: {transformed}")
    
    # Generate speech
    output_file = "test_output.wav"
    success = tts.synthesize_speech_with_phonemes(text, output_file)
    
    if success:
        print(f"\nAudio saved to: {output_file}")
        print("Transformations applied:")
        for exp in result['explanations']:
            print(f"- {exp}")
        for comb in result['combinations']:
            print(f"- {comb}")
    else:
        print("Failed to generate speech")

if __name__ == "__main__":
    test_speak()
