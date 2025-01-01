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
