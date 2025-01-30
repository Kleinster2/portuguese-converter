from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs, urlparse
import logging

# Add the api directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from portuguese_converter import convert_to_phonetic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """Handle incoming requests."""
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
        try:
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
            
            logger.info(f"Converting text: {text}")
            
            # Convert the text using our converter
            try:
                result = convert_to_phonetic(text)
                logger.info(f"Conversion result: {result}")
            except Exception as e:
                logger.error(f"Conversion error: {str(e)}")
                return {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({
                        "success": False,
                        "error": f"Conversion error: {str(e)}"
                    })
                }
            
            # Send success response
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": True,
                    "original": text,
                    "result": result
                })
            }
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
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
            logger.error(f"Internal server error: {str(e)}")
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
