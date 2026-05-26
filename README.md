# Educational Institute Management System

Monorepo for a single-institute educational management platform:

| Component | Stack |
|-----------|--------|
| **Backend** | Django 5, DRF, JWT, Celery, Channels, SQLite/MySQL |
| **Admin Portal** | React 18, Vite, MUI, Zustand |
| **Mobile** | Flutter 3, Riverpod, Dio, Hive |

## Tier labels

- **Tier A (production):** Auth, students, attendance (manual/QR), courses, enrollment, announcements
- **Tier B (functional-lite):** Fees (billing runs, scholarships, late fee, Fonepay ledger, collection desk), **BI Reports**, results (marks + publish approval), student history timeline
- **Tier C (flagged stub):** Online payments (eSewa/Khalti/Connect IPS mock), WebSocket chat, live classes, predictive analytics, library, assignments

Feature flags are controlled via `PATCH /api/v1/admin/features/` (super admin) or Settings page in admin portal.

## Quick start (local)

### Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_all
python manage.py runserver
```

API: http://127.0.0.1:8000/api/v1/  
Swagger: http://127.0.0.1:8000/api/schema/swagger-ui/

**Demo accounts:**

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@institute.edu.np | admin123 |
| Reception | reception@institute.edu.np | reception123 |
| Accountant | accountant@institute.edu.np | accountant123 |
| Teacher | teacher@institute.edu.np | teacher123 |
| Student | student1@institute.edu.np | student123 |
| Parent | parent@institute.edu.np | parent123 |

### Admin portal

```bash
cd admin-portal
npm install
copy .env.example .env
npm run dev
```

Open http://localhost:5173

### Mobile

```bash
cd mobile
flutter pub get
flutter create . --platforms=android   # first time only
flutter run
# Emulator API: http://10.0.2.2:8000/api/v1
# Physical phone: see mobile/BUILD_ANDROID.md (install Android SDK, then build APK)
```

**APK on a real device** — you do **not** need the Android Studio IDE. See [mobile/BUILD_ANDROID.md](mobile/BUILD_ANDROID.md):

- **Command-line SDK only** (small local install), or  
- **GitHub Actions** workflow `Build mobile APK` (cloud build, download artifact), or  
- **Chrome** for a quick UI smoke test (`flutter run -d chrome`)

### Docker (MySQL + Redis + Nginx)

```bash
cd docker
copy ..\backend\.env.example ..\backend\.env
# Edit backend/.env for DB_ENGINE=mysql when using compose
docker compose up --build
```

**Load all demo data** (after compose is up):

```bash
docker compose exec backend python manage.py seed_all
# Or skip heavy fee billing: seed_all --skip-fees
```

Covers students, courses, enrollment, attendance, calendar, fees (billing/Fonepay), results, announcements, library, leave, assignments, communication, biometric, and enables feature flags for testing.

## Tests

```bash
cd backend
pytest
```

## Project structure

```
student-mgmt-system/
├── backend/          # Django apps: accounts, students, courses, enrollment,
│                     # attendance, fees, results, announcements, analytics, etc.
├── admin-portal/     # React admin UI
├── mobile/           # Flutter iOS/Android
├── docker/           # compose, nginx, Dockerfile
└── docs/             # DEPLOYMENT.md
```

## API modules

- `/api/v1/auth/` — JWT login, OTP, register, profile
- `/api/v1/students/` — onboarding, QR, ID card PDF
- `/api/v1/courses/`, `/api/v1/enrollment/`
- `/api/v1/attendance/` — class registers (auto-created by date+batch+course+period), QR/offline, reports, payroll export — see [docs/ATTENDANCE_MODULE.md](docs/ATTENDANCE_MODULE.md)
- `/api/v1/events/` — academic calendar (holidays, breaks, exams, events), bulk CSV, month summary — see [docs/ACADEMIC_CALENDAR_REQUIREMENTS.md](docs/ACADEMIC_CALENDAR_REQUIREMENTS.md)
- `/api/v1/biometric/webhook/` — HMAC-signed device webhook
- `/api/v1/fees/` — billing runs, scholarships, late fee, payments (incl. Fonepay), summary
- `/api/v1/analytics/reports/` — BI reports (students, courses, enrollment, finance)
- `/api/v1/results/` — subject mark sheet, marks register, approval workflow (flagged)
- `/api/v1/courses/subjects/` — program subjects (per semester)
- `/api/v1/features/` — public feature flags

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment.
