#!/bin/sh
set -e

echo "Waiting for database..."
for i in $(seq 1 60); do
  if python - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
connection.ensure_connection()
PY
  then
    echo "Database is ready."
    break
  fi
  echo "Database not ready (${i}/60), retrying in 2s..."
  sleep 2
done

python manage.py migrate --noinput

# Non-fatal: demo data may already exist or hit duplicate rows on re-run.
python manage.py seed_all || python manage.py seed_demo || echo "seed skipped or completed with warnings."

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
