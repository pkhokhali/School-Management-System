# Attendance module — class registers

## Concept

A **class register** (`AttendanceSession`) is one attendance sheet for:

- **Date** + **Batch** + **Course** + **Period** (1, 2, … if the same course meets twice per day)
- Optional **Shift** (usually copied from the batch)

Teachers and reception **do not need to create registers manually** — the system uses `get_or_create` when marking or scanning.

## APIs

| Endpoint | Purpose |
|----------|---------|
| `POST /attendance/sessions/ensure/` | Open register: `{ date, batch, course, period? }` |
| `GET /attendance/sessions/my-classes/?date=` | Teacher assigned classes + auto registers |
| `POST /attendance/records/bulk/` | Bulk mark — `session_id` **or** `date`+`batch`+`course`+`period` |
| `POST /attendance/qr-mark/` | QR scan — same register keys |
| `GET /attendance/reports/students/?from=&to=` | % attendance per student per course |
| `GET /attendance/payroll-summary/?from=&to=` | Payroll foundation (students + teachers) |
| `POST /attendance/payroll-summary/` | Mark eligible rows `payroll_exported_at` |

## Holidays

On institute holidays (academic calendar), **teachers cannot mark**; reception/super admin may mark with a warning.

## Biometric

Webhook should send `course_id` (or configure `default_course` on the device). Optional `period`.

## Payroll (item 7)

- **Students:** present + late days count as payroll-eligible; `payroll_exported_at` after export.
- **Teachers:** class-days = registers in range with at least one student marked.

Full payroll calculation module is separate; this API feeds it.
