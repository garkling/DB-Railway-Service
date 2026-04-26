# Test: Issue Ticket — Success

**Operation:** POST /api/tickets
**Request body:**
- train_number: IC-701
- service_date: 2026-04-01
- passenger_id: P003
- class_code: 2ND
- seat_number: 5C

**Result:** 201 Created. Ticket #5 created.
- price_paid: 270.00 (sourced from operator_class_route_pricing for UZ/2ND/route 1)
- booking_status: confirmed
- payment_method: card

**Affected tables:** ticket
**Before:** see `before_ticket.csv` (4 pre-existing rows for this train)
**After:** see `after_ticket.csv` (one additional row for ticket #5)

**Test verdict:** PASS — INSERT happened atomically; all FK-validated; DB defaults honoured.
