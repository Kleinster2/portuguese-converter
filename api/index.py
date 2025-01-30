def handler(request, context):
    """Simple handler function for Vercel serverless"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": '{"message": "Hello from Python!"}'
    }
