import json
import os
import sys

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from portuguese_converter import convert_text_to_pt

def handler(request):
    """Simple handler function for Vercel serverless"""
    if request.method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Portuguese Converter API is running'})
        }
    
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text = body.get('text', '')
            if not text:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'No text provided'})
                }
            
            converted_text = convert_text_to_pt(text)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'converted_text': converted_text})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            }
