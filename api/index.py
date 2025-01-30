import json
import os
import sys

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def handler(request):
    """Handle incoming requests."""
    try:
        if request.method == "GET":
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "message": "Portuguese Converter API is working",
                    "endpoints": {
                        "GET /": "API information",
                        "POST /api/convert": "Convert Portuguese text to phonetic"
                    }
                })
            }
        
        if request.method == "POST":
            # Parse the request body
            body = json.loads(request.get("body", "{}"))
            
            # Validate input
            if "text" not in body:
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({
                        "success": False,
                        "error": "Missing required field: text"
                    })
                }
            
            text = body["text"]
            if not isinstance(text, str):
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({
                        "success": False,
                        "error": "Text must be a string"
                    })
                }
            
            # For now, just echo back the text
            # We'll add the conversion later once this works
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": True,
                    "original": text,
                    "result": f"Echo: {text}"
                })
            }
        
        # Handle OPTIONS for CORS
        if request.method == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": ""
            }
        
        return {
            "statusCode": 405,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": False,
                "error": "Method not allowed"
            })
        }
        
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": False,
                "error": "Invalid JSON payload"
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            })
        }
