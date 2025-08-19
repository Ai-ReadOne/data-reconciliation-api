#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate

echo "Starting server..."
uvicorn data_reconciliation_api.asgi:application --host 0.0.0.0 --port 8000