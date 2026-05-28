# Institute UI design system

Aligned with `student_app_all_screens.html` (navy header, indigo accent, light cards).

## Tokens

| Token | Value | Use |
|-------|-------|-----|
| Navy | `#1a1a2e` | Headers, drawer, QR screen |
| Indigo | `#4361ee` | Primary actions, active nav |
| Surface | `#f4f6fb` | Page background |
| Card border | `#e8eaf0` | White cards |
| Text | `#1a1a2e` / `#94a3b8` | Primary / muted |

## Mobile (Flutter)

- `mobile/lib/core/theme/student_palette.dart`
- `mobile/lib/features/student/widgets/student_ui.dart` — `StudentNavyHeader`, `StudentCard`, pills, progress bars
- Bottom nav: **Home · Courses · Schedule · Results · Profile**
- Fees, Notices, Attendance, QR: quick actions or pushed screens

## Admin portal (React + MUI)

- `admin-portal/src/theme/instituteBrand.ts`
- `admin-portal/src/theme/theme.ts` — MUI theme
- Navy sidebar, light content area, indigo primary

## Teacher / parent portals

Reuse the same `instituteBrand` tokens when those web surfaces are built.
