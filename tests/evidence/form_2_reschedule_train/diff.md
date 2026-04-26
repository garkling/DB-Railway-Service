# Test: Reschedule Train — Cascade UPDATE

**Operation:** PUT /api/trains/IC-701/2026-04-01
**New PK:** IC-702 / 2026-04-02 (with new scheduled times)

**Goal:** Verify ON UPDATE CASCADE on the composite PK (train_number, service_date)
propagates to `coach` and `ticket` via the FK constraints in 001_initial_schema.sql.

**Cascade reach:**
- train  : 1 row moved (old PK now empty, new PK holds the row)
- coach  : 5 row(s) cascaded (old PK: 0 → new PK: 5)
- ticket : 4 row(s) cascaded (old PK: 0 → new PK: 4)

**Affected tables:** train, coach, ticket
**Before:** see `before_train.csv`, `before_coach.csv`, `before_ticket.csv`
**After:** see `after_train.csv`, `after_coach.csv`, `after_ticket.csv`

**Test verdict:** PASS — cascade UPDATE works correctly across all 3 tables.
