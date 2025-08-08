# Simple API handler for Vercel without Django complexity
import json
import os
from urllib.parse import urlparse, parse_qs

# Set environment variables
os.environ.setdefault('TMDB_API_KEY', os.getenv('TMDB_API_KEY', ''))

def create_response(status_code, data, headers=None):
    """Create a proper HTTP response"""
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(data)
    }

def handler(request):
    """Main Vercel handler"""
    try:
        # Parse the request
        method = getattr(request, 'method', 'GET')
        url = getattr(request, 'url', None)
        path = url.path if url else '/'
        
        # Health check endpoint
        if path == '/api/health/' or path == '/api/health':
            return create_response(200, {
                'status': 'healthy',
                'service': 'movie-recommendation-api',
                'version': '1.0.0',
                'message': 'API is running on Vercel!'
            })
        
        # API documentation redirect
        elif path.startswith('/api/docs'):
            return create_response(200, {
                'message': 'API Documentation',
                'endpoints': {
                    'health': '/api/health/',
                    'movies': '/api/v1/movies/',
                    'genres': '/api/v1/genres/'
                },
                'note': 'Full Django backend coming soon!'
            })
        
        # Admin interface placeholder
        elif path.startswith('/admin'):
            return create_response(200, {
                'message': 'Admin Interface',
                'note': 'Django admin will be available once backend is fully deployed',
                'status': 'placeholder'
            })
        
        # Default response
        else:
            return create_response(404, {
                'error': 'Endpoint not found',
                'path': path,
                'available_endpoints': ['/api/health/', '/api/docs/', '/admin/']
            })
            
    except Exception as e:
        return create_response(500, {
            'error': 'Internal server error',
            'message': str(e),
            'type': 'handler_error'
        })

# Vercel expects the app to be named 'app'
app = handler
