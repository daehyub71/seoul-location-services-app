"""
Vercel Serverless Function Handler - Minimal Test
"""

def handler(event, context):
    """
    Bare-bones Lambda-compatible handler for testing
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': '{"status": "ok", "message": "Basic handler works!"}'
    }
