# Academic year & institute calendar — requirements (College Admin)

Captured from reception / academic office workflow (Nepal + semester colleges).

## Academic year

| Requirement | Detail |
|-------------|--------|
| Define years | Name (e.g. `2081/082` or `2025-2026`), **start** and **end** date |
| One current year | Only one `is_current` at a time — drives default filters (batches, calendar, fees) |
| Link to batches | Batches belong to an academic year (existing) |
| Validation | End date after start; warn if overlapping years (optional) |

## Institute calendar

| Requirement | Detail |
|-------------|--------|
| Event types | **Public holiday**, **Institute holiday**, **Term break**, **Exam period**, **Academic event**, **Admission**, **Meeting / assembly** |
| Date range | Single entry can span multiple days (e.g. Dashain 5 days) |
| Scoped to year | Each entry tied to an **academic year** for reporting |
| Quick mark holiday | Admin selects **from–to** dates + title → one holiday/break entry |
| Bulk upload | CSV: `title,event_type,start_date,end_date,description` — import many rows at once |
| View | Month view + list; filter by type and academic year |
| Visibility | All staff/students **read** calendar; only **admin/reception** can create/edit |
| Downstream (later) | Attendance / payroll skip or flag **institute holidays**; notices on calendar events |

## CSV template (bulk)

```csv
title,event_type,start_date,end_date,description
Dashain,public_holiday,2025-10-20,2025-10-24,National festival
Winter term break,term_break,2025-12-20,2026-01-05,
Board exam week,exam,2026-03-01,2026-03-07,Grade 12
```

`event_type` values: `public_holiday`, `holiday`, `term_break`, `exam`, `event`, `admission`, `meeting`.

## Roles

- **Super admin / reception:** full CRUD, bulk upload, mark holiday range  
- **Teacher / student (mobile & portal):** read-only calendar for planning classes  
