#!/usr/bin/env bash
# Fail on any error
set -o errexit

# Calculate workers based on CPU cores
WORKERS=$((2 * $(nproc) + 1))

echo "--> Starting Gunicorn with $WORKERS workers"
exec gunicorn pendeza.wsgi:application \
  --bind 0.0.0.0:${PORT:-10000} \
  --workers $WORKERS \
  --timeout 120 \
  --log-level=info \
  --access-logfile -