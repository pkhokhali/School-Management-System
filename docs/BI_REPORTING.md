# BI Reporting — Management & Accountant Analytics

**Audience:** Super Admin, Admin Staff / Accountant  
**API:** `GET /api/v1/analytics/reports/`  
**Portal:** **BI Reports** (`/reports`)

---

## Report sections

### Overview
- KPI cards: students, courses, enrollments, batches, departments, teachers, monthly collection
- Fee collection trend (6 months)
- Enrollment status pie chart

### Students
- Students by batch
- Students by department

### Academic
- Approved enrollments by program
- Course capacity utilization (enrolled vs max)

### Finance
- All-time / monthly collection, outstanding, overdue
- Collections by payment mode (cash, Fonepay, eSewa, etc.)

### Operations (accountant desk)
- Pending refund approvals → Fees → Refund workflow
- Installments due in next 7 days (count + NPR)
- Attendance present rate
- Published announcements
- Dropped enrollments

---

## Accountant widgets (also on Dashboard & Fees summary)

| Metric | Source |
|--------|--------|
| Refunds pending | `RefundRequest` status = pending |
| Installments due (7d) | Assignments with due_date in week and balance > 0 |
| Installment amount due | Sum of balances for those assignments |

Dashboard home and **Fees → Summary** show these alongside collection KPIs.

---

## Related endpoints

| Path | Purpose |
|------|---------|
| `/analytics/dashboard/` | Home dashboard (includes accountant ops KPIs) |
| `/analytics/reports/` | Full BI snapshot |
| `/analytics/attendance-trend/` | Daily attendance chart |
| `/analytics/at-risk/` | Predictive at-risk students (feature flag) |
| `/fees/summary/` | Fee desk summary including refunds & installments |

---

## Enable at-risk analytics

Settings → enable `predictive_analytics` for the separate **At-risk analytics** nav item.

BI Reports is always available to roles with `reports` view permission (super admin by default).
