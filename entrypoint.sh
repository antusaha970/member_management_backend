#!/bin/sh
# entrypoint.sh

# Apply database migrations
python manage.py migrate --noinput

# Optionally, collect static files (for production)
python manage.py collectstatic --noinput

# Execute the container's main command
exec "$@"
