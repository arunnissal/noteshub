#!/bin/bash

echo "Building NotesHub for production..."

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser if needed (optional)
# python manage.py createsuperuser --noinput

echo "Build completed successfully!" 