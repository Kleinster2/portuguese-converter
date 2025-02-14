#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Test script for TTS integration."""

import os
from api.tts_converter import word_to_ipa, convert_to_ssml
import azure.cognitiveservices.speech as speechsdk
import requests

def test_ipa_conversion():
    """Test IPA phoneme conversion with various words."""
    test_words = [
        "olá",
        "não",
        "muito",
        "trabalho",
        "manhã",
        "português",
        "coração",
        "você",
        "tá",
        "aqui"
    ]
    
    print("\n=== Testing IPA Conversion ===")
    print("╔" + "═" * 30 + "╦" + "═" * 30 + "╗")
    print("║ {:<28} ║ {:<28} ║".format("Original Word", "IPA"))
    print("╠" + "═" * 30 + "╬" + "═" * 30 + "╣")
    
    for word in test_words:
        ipa = word_to_ipa(word)
        print("║ {:<28} ║ {:<28} ║".format(word, ipa))
    
    print("╚" + "═" * 30 + "╩" + "═" * 30 + "╝")

def format_ssml(ssml):
    """Format SSML for display with proper indentation and line breaks."""
    import xml.dom.minidom
    
    # Parse and pretty print the SSML
    try:
        dom = xml.dom.minidom.parseString(ssml)
        pretty_ssml = dom.toprettyxml(indent="  ")
        # Remove empty lines and normalize line endings
        lines = [line for line in pretty_ssml.split("\n") if line.strip()]
        # Truncate lines that are too long
        formatted_lines = []
        for line in lines:
            if len(line) > 65:
                formatted_lines.append(line[:62] + "...")
            else:
                formatted_lines.append(line)
        return formatted_lines
    except:
        # If XML parsing fails, return original with basic formatting
        return [line for line in ssml.replace("><", ">\n<").split("\n")]

def test_ssml_generation():
    """Test SSML generation with sample sentences."""
    test_sentences = [
        "Olá, como vai você?",
        "Não estou entendendo nada.",
        "O português é muito difícil.",
        "Tá tudo bem aqui.",
    ]
    
    print("\n=== Testing SSML Generation ===")
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\nTest Case {i}:")
        print("┌" + "─" * 68 + "┐")
        print("│ Input:                                                                  │")
        print("│ {:<66} │".format(sentence))
        print("├" + "─" * 68 + "┤")
        print("│ SSML Output:                                                           │")
        
        # Generate and format SSML
        ssml = convert_to_ssml(sentence)
        formatted_lines = format_ssml(ssml)
        
        # Print each line with proper box drawing
        for line in formatted_lines:
            print("│ {:<66} │".format(line))
        
        print("└" + "─" * 68 + "┘")

def test_azure_tts(subscription_key=None, region=None):
    """
    Test Azure TTS integration.
    
    Args:
        subscription_key (str): Azure Speech Service subscription key
        region (str): Azure region (e.g., 'eastus')
    """
    # Check for credentials in environment variables if not provided
    subscription_key = subscription_key or os.getenv("AZURE_SPEECH_KEY")
    region = region or os.getenv("AZURE_SPEECH_REGION")
    
    if not subscription_key or not region:
        print("\n=== Skipping Azure TTS Test ===")
        print("┌" + "─" * 68 + "┐")
        print("│ Azure credentials not found. To test TTS:                               │")
        print("│                                                                        │")
        print("│ 1. Set environment variables:                                          │")
        print("│    - AZURE_SPEECH_KEY                                                  │")
        print("│    - AZURE_SPEECH_REGION                                              │")
        print("│                                                                        │")
        print("│ 2. Or pass credentials to this function                               │")
        print("└" + "─" * 68 + "┘")
        return
    
    print("\n=== Testing Azure TTS Integration ===")
    print("┌────────────────────────────────────────────────────────────────────┐")
    print("│ Initializing Azure TTS...                                              │")
    
    # Get credentials from environment
    subscription_key = os.getenv('AZURE_SPEECH_KEY')
    region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
    
    if not subscription_key:
        print("│ ✗ Error: AZURE_SPEECH_KEY environment variable not set              │")
        return
        
    # First try REST API approach
    endpoint = "https://eastus.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-32kbitrate-mono-mp3'
    }
    
    # Simple SSML for testing
    ssml = """
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='pt-BR'>
        <voice name='pt-BR-FranciscaNeural'>
            Olá! Como vai você?
        </voice>
    </speak>
    """
    
    try:
        response = requests.post(endpoint, headers=headers, data=ssml.encode('utf-8'))
        print("│ REST API Status Code: {:<45} │".format(response.status_code))
        
        if response.status_code == 200:
            print("│ ✓ REST API test successful!                                         │")
            with open('test_output.mp3', 'wb') as f:
                f.write(response.content)
            print("│ ✓ Audio saved to test_output.mp3                                    │")
        else:
            print("│ ✗ REST API test failed with status code: {:<25} │".format(response.status_code))
            print("│   Error: {:<52} │".format(response.text[:52]))
            
        # Now try the SDK approach with simpler configuration
        speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key,
            region=region
        )
        
        # Set synthesis language and voice
        speech_config.speech_synthesis_language = "pt-BR"
        speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"
        
        # Create audio output config
        audio_config = speechsdk.audio.AudioOutputConfig(filename="sdk_output.wav")
        
        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        # Test sentence
        text = "Olá! Como vai você? Tá tudo bem aqui no Brasil."
        print("│                                                                        │")
        print("│ Converting to speech:                                                 │")
        print("│ {:<66} │".format(text))
        
        # Try basic synthesis first
        result = synthesizer.speak_text_async(text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("│ ✓ Basic synthesis succeeded!                                          │")
            print("│ ✓ Audio saved to sdk_output.wav                                      │")
            
            # Now try with SSML
            ssml = convert_to_ssml(text)
            
            # Create new audio config for SSML synthesis
            ssml_audio_config = speechsdk.audio.AudioOutputConfig(filename="ssml_output.wav")
            ssml_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=ssml_audio_config
            )
            
            result = ssml_synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("│ ✓ SSML synthesis succeeded!                                          │")
                print("│ ✓ Audio saved to ssml_output.wav                                    │")
            else:
                print("│ ✗ SSML synthesis failed: {:<35} │".format(str(result.reason)))
                if result.cancellation_details:
                    print("│   Error: {:<52} │".format(
                        str(result.cancellation_details.error_details)[:52]))
        else:
            print("│ ✗ Basic synthesis failed: {:<35} │".format(str(result.reason)))
            if result.cancellation_details:
                print("│   Error: {:<52} │".format(
                    str(result.cancellation_details.error_details)[:52]))
    
    except Exception as e:
        print("│ ✗ Error: {:<52} │".format(str(e)[:52]))
    
    print("└" + "─" * 68 + "┘")

def main():
    """Run all tests."""
    # Test IPA conversion
    test_ipa_conversion()
    
    # Test SSML generation
    test_ssml_generation()
    
    # Test Azure TTS (will skip if no credentials)
    test_azure_tts()

if __name__ == "__main__":
    main()
