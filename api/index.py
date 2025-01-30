def handler(request):
    if request.get('method') == 'GET':
        return {
            'statusCode': 200,
            'body': 'Hello from Python!'
        }
    return {
        'statusCode': 405,
        'body': 'Method not allowed'
    }
