# Student Mobile App — UI/UX (implemented)

Design reference: `student_mobile_app_ux.html` (teal/mint dark theme).

## Navigation (5 tabs)

| Tab | Screen |
|-----|--------|
| Home | Week-at-a-glance hero, quick actions, notices |
| Courses | Enrolled programs + progress bars |
| Fees | Due/paid summary, breakdown, Fonepay CTA |
| Results | GPA summary, subject grades |
| Study | Exam countdown, attendance bars, calendar/syllabus |

Profile: light-themed screen via avatar (top-right on Home).

## Data sources

- `/students/` — profile, batch, roll
- `/enrollment/?status=approved` — courses
- `/fees/assignments/` — fees tab
- `/results/marks/` — results + GPA estimate
- `/results/exams/` — study hub countdown
- `/announcements/` — home notices
- `/events/calendar/month/` — study hub calendar sheet

## Phase 2 (not in UI yet)

- Teacher-filled batch course progress API
- Certificate requests
- Push notifications at 75% attendance
- Full attendance % from dedicated student API
