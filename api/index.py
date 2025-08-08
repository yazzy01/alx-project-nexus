import json
import os
import sys
import logging
from http import HTTPStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def create_response(status_code, body, content_type='application/json'):
    """Helper function to create a response dictionary."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': content_type,
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body) if isinstance(body, dict) else body
    }

def handle_health():
    """Handle health check requests."""
    return create_response(
        HTTPStatus.OK,
        {
            'status': 'ok',
            'message': 'Server is running',
            'version': '1.0.0',
            'environment': os.getenv('VERCEL_ENV', 'development')
        }
    )

def handle_api(path):
    """Handle API requests."""
    try:
        # This is a simple example - replace with your actual API logic
        return create_response(
            HTTPStatus.OK,
            {
                'status': 'success',
                'message': 'API endpoint',
                'path': path,
                'data': []
            }
        )
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return create_response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            {'error': 'Internal server error'}
        )

def handle_admin():
    """Handle admin interface requests."""
    return create_response(
        HTTPStatus.OK,
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Interface</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; text-align: center; }
                h1 { color: #333; }
                .status { color: #4CAF50; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Admin Interface</h1>
                <p>Admin interface would be served here</p>
                <p class="status">Status: <span>Connected</span></p>
            </div>
        </body>
        </html>
        """,
        'text/html'
    )

def handle_docs():
    """Handle API documentation requests."""
    return create_response(
        HTTPStatus.OK,
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                h1 { color: #333; }
                .endpoint { 
                    background: #f5f5f5; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 5px;
                }
                .method { 
                    display: inline-block; 
                    padding: 3px 8px; 
                    border-radius: 3px; 
                    color: white;
                    font-weight: bold;
                    margin-right: 10px;
                }
                .get { background: #61AFFE; }
                .post { background: #49CC90; }
                .put { background: #FCA130; }
                .delete { background: #F93E3E; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>API Documentation</h1>
                <p>Interactive API documentation would be served here</p>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/health</strong> - Health check endpoint
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/movies</strong> - List all movies
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/movies/{id}</strong> - Get movie details
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <strong>/api/movies</strong> - Add a new movie
                </div>
            </div>
        </body>
        </html>
        """,
        'text/html'
    )

def handle_not_found(path):
    """Handle 404 Not Found errors."""
    return create_response(
        HTTPStatus.NOT_FOUND,
        {
            'status': 'error',
            'message': 'Not found',
            'path': path
        }
    )

def handle_error(e):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {str(e)}")
    return create_response(
        HTTPStatus.INTERNAL_SERVER_ERROR,
        {
            'status': 'error',
            'message': 'Internal server error',
            'error': str(e)
        }
    )

def handler(event, context):
    """Main Lambda/Serverless function handler."""
    try:
        # Log the incoming event for debugging
        logger.info(f"Received event: {json.dumps(event, indent=2)}")
        
        # Extract the path from the event
        path = event.get('path', '')
        http_method = event.get('httpMethod', 'GET')
        
        # Handle preflight OPTIONS request for CORS
        if http_method == 'OPTIONS':
            return create_response(HTTPStatus.NO_CONTENT, {})
        
        # Route the request based on the path
        if path in ['/api/health', '/health']:
            return handle_health()
        elif path.startswith('/api/'):
            return handle_api(path)
        elif path == '/admin' or path.startswith('/admin/'):
            return handle_admin()
        elif path == '/docs' or path.startswith('/docs'):
            return handle_docs()
        else:
            return handle_not_found(path)
            
    except Exception as e:
        return handle_error(e)
