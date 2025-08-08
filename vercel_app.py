from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def handle_request(self):
        try:
            # Parse the request path
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            # Set response headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Health check endpoint
            if path == '/api/health/' or path == '/api/health':
                response = {
                    'status': 'healthy',
                    'service': 'movie-recommendation-api',
                    'version': '1.0.0',
                    'message': 'API is running on Vercel!'
                }
            
            # API documentation
            elif path.startswith('/api/docs'):
                response = {
                    'message': 'API Documentation',
                    'endpoints': {
                        'health': '/api/health/',
                        'movies': '/api/v1/movies/',
                        'genres': '/api/v1/genres/'
                    },
                    'swagger_ui': 'Available at /api/docs/',
                    'redoc': 'Available at /api/redoc/',
                    'note': 'Basic API endpoints are working!'
                }
            
            # Admin interface
            elif path.startswith('/admin'):
                response = {
                    'message': 'Admin Interface',
                    'note': 'Django admin interface placeholder',
                    'status': 'available',
                    'login_url': '/admin/login/'
                }
            
            # API endpoints placeholder
            elif path.startswith('/api/'):
                response = {
                    'message': 'API Endpoint',
                    'path': path,
                    'method': self.command,
                    'note': 'API endpoint is working!',
                    'available_endpoints': ['/api/health/', '/api/docs/', '/admin/']
                }
            
            # Default response
            else:
                self.send_response(404)
                response = {
                    'error': 'Endpoint not found',
                    'path': path,
                    'available_endpoints': ['/api/health/', '/api/docs/', '/admin/']
                }
            
            # Send JSON response
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                'error': 'Internal server error',
                'message': str(e),
                'type': 'handler_error'
            }
            self.wfile.write(json.dumps(error_response).encode())
