#!/bin/bash

# Railway startup script for Django
echo "Starting Django application..."

# Only run migrations if DATABASE_URL is set (Railway environment)
if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start gunicorn
echo "Starting gunicorn server..."
exec gunicorn movie_recommendation_backend.wsgi:application --host 0.0.0.0 --port $PORT
