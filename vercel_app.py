import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set environment variables for Vercel
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommendation_backend.settings')
os.environ.setdefault('VERCEL', '1')

# Initialize Django
import django
from django.core.wsgi import get_wsgi_application

# Setup Django
django.setup()

# Get the WSGI application
application = get_wsgi_application()

# Vercel expects the app to be named 'app'
app = application
