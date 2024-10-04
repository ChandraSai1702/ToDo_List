#!/bin/sh

# Wait for the database to be ready (useful for databases like PostgreSQL or MySQL)
# Replace 'db' with your database hostname and '5432' with your database port
echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done

# Apply database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start the application
echo "Starting the Django server..."
exec "$@"
