# -*- coding: utf-8 -*-
import requests
import json
import os
from openai import OpenAI

# Load environment variables
# Removed load_dotenv() as per instruction

# Get API key from environment
api_key = os.getenv('OPENAI_API_KEY')
org_id = "org-Y523VzNzWZ8wEGgYYVjhBBHw"  # Organization ID from project API key

client = OpenAI(
    api_key=api_key,
    organization=org_id
)

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello, can you confirm my API key is working?"}]
    )
    print("Success! API key is working.")
    print("Response:", response)
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'response'):
        try:
            error_msg = e.response.json().get('error', {}).get('message', str(e))
            print("Full error message:", error_msg)
        except:
            pass

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
