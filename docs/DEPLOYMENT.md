# Deployment Guide

## Backend (VPS — Nginx + Gunicorn)

1. Provision Ubuntu 22.04+ with MySQL 8 and Redis.
2. Clone repo, create virtualenv, install `backend/requirements.txt`.
3. Set environment variables (see `backend/.env.example`):
   - `DEBUG=False`
   - `SECRET_KEY` (strong random)
   - `DB_ENGINE=mysql` and MySQL credentials
   - `USE_REDIS=True`
   - `ALLOWED_HOSTS=your-domain.com`
   - `CORS_ALLOWED_ORIGINS=https://admin.your-domain.com`
4. Run migrations and collect static:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py seed_demo  # optional
   ```
5. Gunicorn systemd unit:
   ```bash
   gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
   ```
6. Celery worker + beat for scheduled announcements and reminders.
7. Nginx reverse proxy:
   - `/api/` → Gunicorn
   - `/media/` → filesystem or S3
   - TLS via Let's Encrypt (certbot)

## Admin portal (Vercel / Netlify)

```bash
cd admin-portal
npm run build
```

Set `VITE_API_URL=https://api.your-domain.com/api/v1` in hosting environment.

Deploy `dist/` folder.

## Mobile (Play Store / App Store)

```bash
cd mobile
flutter build appbundle   # Android
flutter build ipa         # iOS (macOS + Xcode)
```

- Add `google-services.json` for Firebase Cloud Messaging.
- Configure signing keys in Android `key.properties` and iOS provisioning.
- Privacy policy URL required for store listing.
- Point production build to API:
  ```bash
  flutter build appbundle --dart-define=API_BASE_URL=https://api.your-domain.com/api/v1
  ```

## Docker Compose (all-in-one)

From `docker/`:

```bash
docker compose up --build
```

- API: http://localhost:8000
- Admin (after `npm run build` in admin-portal): http://localhost/

## Backup

- Schedule `mysqldump` nightly to encrypted storage.
- Document point-in-time recovery with MySQL binlogs for production.
- Media files: sync `media/` to S3-compatible storage.

## Biometric webhook

Set `BIOMETRIC_WEBHOOK_SECRET` and send header `X-Signature: HMAC-SHA256(body)`.

Payload:

```json
{"user_id": "device_user_1", "timestamp": "2025-05-25T10:00:00Z", "device_id": "DEV001", "status": "present"}
```

## Security checklist

- [ ] Rotate `SECRET_KEY` and webhook secret
- [ ] Restrict `ALLOWED_HOSTS` and CORS
- [ ] Enable HTTPS only
- [ ] Rate limiting enabled (DRF throttling)
- [ ] File upload size limits at Nginx
