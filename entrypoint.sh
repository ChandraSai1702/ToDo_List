#!/bin/sh

# Apply database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start the application
echo "Starting the Django server..."
exec "$@"
