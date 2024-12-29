# -*- coding: utf-8 -*-
import requests
import json

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
    "casa escura",  # Testing a + e combination
    "sobre a mesa",  # Testing e + a combination
    "muito alto",   # Testing o + a combination
    "para ela"      # Testing a + e combination
]

print("Testing Portuguese Text Converter API...")
for test in test_cases:
    test_conversion(test)
