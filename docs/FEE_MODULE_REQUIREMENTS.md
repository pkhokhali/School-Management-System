# Fee Module — College Accountant / CA Requirements

**Document owner:** College Accountant / CA  
**Audience:** Senior Developer  
**Module tier:** B (offline + Fonepay; full online init feature-flagged)  
**Version:** 2.0 — May 2026

---

## 1. Business context

Accounts must **bill by batch or semester**, apply **scholarships** and **late fees**, collect via **multiple payment modes** (cash, cheque, eSewa, Khalti, Connect IPS, **Fonepay**), and keep a reconcilable **student ledger** and **payment register**.

---

## 2. Roles

| Role | View | Collect | Billing runs | Policies | Setup |
|------|------|---------|--------------|----------|-------|
| Super Admin | Yes | Yes | Yes | Yes | Yes |
| Admin Staff | Yes | Yes | Yes | Yes | Yes |
| Teacher | No | No | No | No | No |

---

## 3. Core workflows

### 3.1 Setup
- **Fee heads** (TUITION, EXAM, LAB…)
- **Fee structures**: program + optional batch + **semester** + head + amount (NPR)

### 3.2 Billing (auto / manual)
1. **Billing run** (`POST /fees/billing-runs/execute/`): filter by batch, program, semester; set due date; optional default scholarship applied to all new bills.
2. **Installment billing**: set `installments` and `interval_days` to split each structure amount into multiple dated ledger rows.
3. **Quick bill** (`POST /fees/assignments/bulk-from-enrollment/`): legacy one-shot from enrollments.
4. Manual assignment row for exceptions.

### 3.3 Scholarships & late fee
- **Scholarship**: percent or fixed NPR; optional scope to one fee head.
- **Late fee policy**: grace days after due date, then rate % + flat on outstanding balance.
- **Apply late fees** (`POST /fees/assignments/apply-late-fees/`): batch update overdue assignments.

### 3.4 Collection
- Record payment with **mode**; for Fonepay store **gateway_ref** / txn id on ledger.
- **Fonepay initiate** (`POST /fees/online/initiate/`) opens gateway URL when `payments_online` is enabled.
- **Fonepay confirm** (`POST /fees/fonepay/confirm/`) when payment completes via gateway callback (feature `payments_online`).
- Receipt PDF per payment.

### 3.5 Refund workflow
- Raise refund requests against a payment.
- Approve / reject by admin-accountant role.
- Complete refund updates student ledger paid/balance values.

### 3.6 Reporting
- Summary: collected today/month, **fonepay_today**, outstanding, overdue, paid/pending counts.
- Payments register with mode label and gateway reference.

---

## 4. API

| Method | Path | Purpose |
|--------|------|---------|
| CRUD | `/fees/heads/` | Fee heads |
| CRUD | `/fees/structures/` | Structures (incl. semester) |
| CRUD | `/fees/assignments/` | Student ledger |
| POST | `/fees/assignments/bulk-from-enrollment/` | Quick bill |
| POST | `/fees/assignments/apply-late-fees/` | Apply late fees |
| CRUD | `/fees/scholarships/` | Scholarships |
| CRUD | `/fees/late-fee-policies/` | Late fee rules |
| GET/POST | `/fees/billing-runs/` | History |
| POST | `/fees/billing-runs/execute/` | Run semester/batch billing |
| CRUD | `/fees/payments/` | Payment register |
| POST | `/fees/online/initiate/` | Start gateway payment |
| POST | `/fees/fonepay/confirm/` | Confirm Fonepay txn |
| CRUD + actions | `/fees/refunds/` | Refund request workflow |
| GET | `/fees/summary/` | Dashboard stats |

---

## 5. Admin portal tabs

1. **Summary** — includes Fonepay today  
2. **Billing runs** — execute + history  
3. **Student ledger** — collect, apply late fees, quick bill  
4. **Payments register** — mode + gateway ref  
5. **Refund workflow** — request / approve / complete  
6. **Scholarships & late fee** — policies CRUD  
7. **Fee structures** & **Fee heads**

Student drawer **Fees** tab: outstanding, collect (incl. Fonepay), link to full fees page.

---

## 6. Demo data

```bash
docker compose exec backend python manage.py migrate fees
docker compose exec backend python manage.py seed_fee_demo
```

Seeds: merit scholarship, semester structures, billing run with installments, overdue + late fee sample, cash/Fonepay payments, and sample refund request.

---

## 7. Acceptance criteria

- [ ] Billing run creates assignments per structure match (program/batch/semester).
- [ ] Scholarship discount reflected on assignment `discount_amount` / balance.
- [ ] Late fee increases balance on overdue rows after apply.
- [ ] Fonepay payment shows mode Fonepay and gateway ref in register and student ledger.
- [ ] Summary `fonepay_today` matches today's Fonepay payments.
