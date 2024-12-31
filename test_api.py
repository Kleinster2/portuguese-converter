# -*- coding: utf-8 -*-
import requests
import json
from api.portuguese_converter import convert_text, AIModel
import pytest
import os

def test_conversion(text):
    url = "https://portuguese-converter.vercel.app/api/portuguese_converter"
    response = requests.post(url, json={"text": text})
    print(f"\nInput: {text}")
    if response.status_code == 200:
        result = response.json()
        print(f"Output: {result['result']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Test cases focusing on vowel combinations
test_cases = [
    "casa escura",     # a + e
    "casa inteira",    # a + i
    "casa onde",       # a + o
    "casa útil",       # a + u
    "casa amarela",    # a + a
    "sobre isso",      # e + i
    "como é",          # o + é
    "para ela"         # a + e after reduction
]

print("Testing Portuguese Text Converter API...")
for test in test_cases:
    test_conversion(test)

def test_basic_conversion():
    assert convert_text("carro") == "carru"
    assert convert_text("mais amor") == "maizamor"
    assert convert_text("não") == "nãum"

@pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OpenAI API key not found")
def test_gpt35_conversion():
    result = convert_text("mais amor", model=AIModel.GPT35)
    assert result.lower() in ["maizamor", "maiz amor"]  # Allow some flexibility in AI output

@pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OpenAI API key not found")
def test_gpt4_conversion():
    result = convert_text("não sei", model=AIModel.GPT4)
    assert result.lower() in ["nãum sei", "nãun sei", "nãum sey"]  # Allow some flexibility in AI output
