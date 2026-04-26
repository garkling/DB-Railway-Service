# Test: Cancel Ticket — Success

**Operation:** DELETE /api/tickets/IC-701/2026-04-01/1
**Result:** 204 No Content (empty body).

**Row counts:**
- ticket total: 16 → 15 (−1)
- target row (IC-701/2026-04-01/#1): 1 → 0
- sibling rows on same train (IC-701/2026-04-01/#2,#3,#4): 3 → 3 (untouched)

**Affected tables:** ticket
**Before:** see `before_ticket.csv` (16 rows)
**After:** see `after_ticket.csv` (15 rows)

**Test verdict:** PASS — DELETE removed exactly one row, no side effects on siblings.
