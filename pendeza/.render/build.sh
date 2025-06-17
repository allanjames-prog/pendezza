#!/usr/bin/env bash
# Fail on any error
set -o errexit

echo "--> Installing dependencies"
pip install -r requirements.txt

# Only run migrations if this isn't a static file build
if [ "$RENDER_SERVICE_TYPE" != "web" ]; then
  echo "--> Skipping migrations for non-web service"
else
  echo "--> Running migrations"
  python manage.py migrate --noinput
fi

echo "--> Collecting static files"
python manage.py collectstatic --noinput

echo "--> Build completed"