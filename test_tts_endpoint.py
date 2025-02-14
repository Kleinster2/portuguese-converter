import requests
import os
import time

def test_tts_endpoint():
    # Test cases with both original and colloquial forms
    test_cases = [
        "Muito obrigado",  # Original
        "Mũyntu ubrigadu",  # Colloquial
        "Como você está?",  # Original
        "Comu cê tá?",     # Colloquial
    ]
    
    for text in test_cases:
        print(f"\nTesting TTS for: {text}")
        
        # Make request to TTS endpoint
        response = requests.post(
            'http://localhost:5000/api/tts',
            json={'text': text}
        )
        
        # Check response
        if response.status_code == 200:
            # Save audio file
            filename = f"test_output_{int(time.time())}.wav"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✓ Success! Audio saved to {filename}")
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.json())
        
        # Wait a bit between requests
        time.sleep(1)

if __name__ == "__main__":
    test_tts_endpoint()
