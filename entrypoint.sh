#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "PostgreSQL started"

echo "Running migrations"
python manage.py migrate


echo "Starting Gunicorn..."
gunicorn kaaizen.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120