import requests
import json

def test_api():
    url = "https://portuguese-converter.vercel.app/api/portuguese_converter"
    
    # Test case 1: Simple text
    payload1 = {
        "text": "Olá, como você está? Estou bem. Tudo otimo."
    }
    
    # Test case 2: Complex text
    payload2 = {
        "text": "Olá, amigos! Estamos aqui para falar sobre os gatos que vivem no jardim."
    }
    
    print("\nTest 1 - Simple text:")
    try:
        response = requests.post(url, json=payload1)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\nTest 2 - Complex text:")
    try:
        response = requests.post(url, json=payload2)
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api()
