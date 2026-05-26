# Results Module — College Coordinator Requirements

**Document owner:** College Co-ordinator  
**Audience:** Senior Developer, QA, Product  
**Module tier:** B (`results_publishing` feature flag)  
**Version:** 1.0 — May 2026

---

## 1. Business context

Results must reflect **what each student is actually studying** — their **approved enrollment in a program (course)**, broken down by **subjects** offered in that program per semester. Marks are not anonymous “exam IDs”; staff work from **program → semester → exam type → batch → student × subject grid**.

Publishing follows institute policy: entry → review → publish (existing approval stages retained).

---

## 2. Roles and permissions

| Role | View results | Enter / edit marks | Manage subjects (syllabus units) | Publish / approve |
|------|--------------|--------------------|----------------------------------|-------------------|
| **Super Admin** | Yes | Yes | Yes | Yes |
| **Admin Staff (Reception)** | Yes | Yes | Yes | No (unless promoted) |
| **Teacher** | Yes (assigned programs only) | Yes (assigned programs only) | No | Submit for review |
| **Student / Parent** | Published marks only (mobile/API) | No | No | No |

**Rule:** Only users with an **approved enrollment** in the selected program may receive marks for that program’s subjects.

**Teacher scope:** Teachers see and enter marks only for **programs (courses) where they have a `TeacherAssignment`** (optionally scoped by batch when assignment includes batch).

---

## 3. Core entities

| Entity | Description |
|--------|-------------|
| **Program (Course)** | Degree/diploma program (e.g. BSc CS) — already in `courses.Course` |
| **Course Subject** | Teaching unit within a program: code, name, semester, credits, max internal/external marks |
| **Enrollment** | Student ↔ program link (`approved` required for mark entry) |
| **Exam** | Assessment event: program + **subject** + exam type + academic term |
| **Mark entry** | One row per student per exam: internal + external marks → auto grade from active grade policy |

---

## 4. Functional requirements

### 4.1 Program subjects (setup)

- CRUD subjects under a program: `code`, `name`, `semester` (1–N), `credit_hours`, `max_internal`, `max_external`, `is_active`.
- Unique subject code per program.
- List/filter by program and semester.

### 4.2 Mark entry (primary workflow)

**Filters (required):**

1. Program (course)  
2. Semester  
3. Exam type: Internal / Mid Term / Final  
4. Academic term (e.g. `Fall 2025`)  
5. Batch (optional — limits to enrolled students in that batch)

**Grid:**

- Rows: students with **approved** enrollment in the program (and batch if selected).  
- Columns: active subjects for that program + semester.  
- Cells: internal marks, external marks (validated ≤ subject maxima).  
- Show computed grade and total per cell after save.

**Save:**

- Upsert marks in bulk; auto-create exam records per subject if missing.  
- Record `entered_by`; link mark to enrollment where possible.  
- Reject marks for students not enrolled in the program.

### 4.3 Marks register (audit)

- Searchable list: student name, program, subject, exam type, term, internal, external, grade, entered by, published flag.
- Filter by program, batch, semester, exam type, term.
- Edit single row (roles with `edit` on results module).

### 4.4 Publishing (admin UI: Results → **Publish & approval** tab)

- Retain approval stages: Marks entered → Teacher → HOD → Admin → Published.  
- **Submit for approval** on each exam session after marks are entered.  
- Role-gated **Approve** button advances one stage; final stage sets `is_published`.  
- MUI horizontal stepper per exam (per SMS Development Prompts doc).  
- When published, students see marks via API (published exams only).

### 4.5 Reports (phase 1)

- Pass % and top performers per exam (existing analysis endpoint).  
- PDF marksheet per student per exam (existing); future: semester marksheet across all subjects.

---

## 5. API contract (summary)

| Method | Path | Purpose |
|--------|------|---------|
| CRUD | `/api/v1/courses/subjects/` | Program subjects |
| GET/POST | `/api/v1/results/mark-sheet/` | Load grid / bulk save marks |
| CRUD | `/api/v1/results/marks/` | Single mark rows (enriched fields) |
| CRUD | `/api/v1/results/exams/` | Exam management |
| CRUD | `/api/v1/results/approvals/` | Workflow |
| GET | `/api/v1/results/analysis/?exam_id=` | Analytics |

**Auth:** JWT + `results_publishing` feature flag.  
**Write:** `super_admin`, `admin_staff`, `teacher` (teacher scoped to assignments).

---

## 6. Admin portal UX

**Route:** `/results`  
**Tabs:**

1. **Enter marks** — filters + editable grid (primary).  
2. **Marks register** — DataTable with filters.  
3. **Program subjects** — CRUD (Super Admin & Admin Staff).

Nav visibility: `results` module `view`. Buttons: `create` / `edit` per role matrix.

---

## 7. Non-functional

- Validate mark totals against subject caps.  
- Idempotent bulk save (same student/subject/exam overwrites).  
- OpenAPI annotations on new endpoints.  
- Seed demo: ≥3 subjects for demo program, sample marks for enrolled students.

---

## 8. Acceptance criteria

- [ ] Admin staff can open Enter marks and save marks for all subjects in a semester.  
- [ ] Teacher sees only assigned programs in course dropdown.  
- [ ] Marks cannot be saved for a student without approved enrollment in selected program.  
- [ ] Marks register shows program, subject, and student names (not raw IDs).  
- [ ] Student API returns only published exam marks.  
- [ ] Feature flag off → module shows enable message, API returns feature disabled.

---

## 9. Out of scope (v1)

- Online re-evaluation requests  
- Integration with assignment marks  
- GPA transcript PDF across full program  
- Parent mobile marks UI (stub remains)
