import requests
import json

response = requests.post('http://localhost:5000/convert', 
                       json={'text': 'vamos'})
print(f"Response: {response.json()}")
