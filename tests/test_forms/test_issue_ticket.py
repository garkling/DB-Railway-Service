from decimal import Decimal

from sqlalchemy import text

from tests.helpers.snapshots import capture_evidence, write_diff_summary

TEST_NAME = "form_1_issue_ticket"
AFFECTED_TABLES = ["ticket"]


def test_issue_ticket_succeeds(engine, isolated_client) -> None:
    """Issuing a ticket for P003 / IC-701 / 2026-04-01 / 2ND / seat 5C inserts one
    new row in the ticket table with the pricing-derived price_paid and the DB
    defaults for booking_status (`confirmed`) and payment_method (`card`)."""
    capture_evidence(engine, TEST_NAME, AFFECTED_TABLES, "before")

    response = isolated_client.post("/api/tickets", json={
        "train_number": "IC-701",
        "service_date": "2026-04-01",
        "passenger_id": "P003",
        "class_code": "2ND",
        "seat_number": "5C",
    })

    capture_evidence(engine, TEST_NAME, AFFECTED_TABLES, "after")

    assert response.status_code == 201
    body = response.json()
    assert body["train_number"] == "IC-701"
    assert body["service_date"] == "2026-04-01"
    assert body["passenger_id"] == "P003"
    assert body["class_code"] == "2ND"
    assert body["seat_number"] == "5C"
    assert Decimal(body["price_paid"]) == Decimal("270.00")
    assert body["booking_status"] == "confirmed"
    assert body["payment_method"] == "card"

    with engine.connect() as conn:
        before_rows = conn.execute(text(
            "SELECT COUNT(*) FROM ticket WHERE train_number='IC-701' "
            "AND service_date='2026-04-01' AND ticket_number < :tn"
        ), {"tn": body["ticket_number"]}).scalar()

    write_diff_summary(TEST_NAME, f"""# Test: Issue Ticket — Success

**Operation:** POST /api/tickets
**Request body:**
- train_number: IC-701
- service_date: 2026-04-01
- passenger_id: P003
- class_code: 2ND
- seat_number: 5C

**Result:** 201 Created. Ticket #{body['ticket_number']} created.
- price_paid: {body['price_paid']} (sourced from operator_class_route_pricing for UZ/2ND/route 1)
- booking_status: {body['booking_status']}
- payment_method: {body['payment_method']}

**Affected tables:** ticket
**Before:** see `before_ticket.csv` ({before_rows} pre-existing rows for this train)
**After:** see `after_ticket.csv` (one additional row for ticket #{body['ticket_number']})

**Test verdict:** PASS — INSERT happened atomically; all FK-validated; DB defaults honoured.
""")


def test_issue_ticket_passenger_not_found(engine, isolated_client) -> None:
    """Issuing a ticket for a non-existent passenger returns 404 PassengerNotFound
    and inserts NO row (transaction rolls back before the INSERT statement)."""
    with engine.connect() as conn:
        before = conn.execute(text("SELECT COUNT(*) FROM ticket")).scalar()

    response = isolated_client.post("/api/tickets", json={
        "train_number": "IC-701",
        "service_date": "2026-04-01",
        "passenger_id": "P999",
        "class_code": "2ND",
    })

    with engine.connect() as conn:
        after = conn.execute(text("SELECT COUNT(*) FROM ticket")).scalar()

    assert response.status_code == 404
    assert response.json()["error"] == "PassengerNotFound"
    assert before == after, "no row should have been inserted on validation failure"


def test_issue_ticket_train_not_found(engine, isolated_client) -> None:
    """Issuing a ticket for a non-existent train returns 404 TrainNotFound
    and inserts NO row."""
    with engine.connect() as conn:
        before = conn.execute(text("SELECT COUNT(*) FROM ticket")).scalar()

    response = isolated_client.post("/api/tickets", json={
        "train_number": "ZZ-999",
        "service_date": "2026-04-01",
        "passenger_id": "P001",
        "class_code": "2ND",
    })

    with engine.connect() as conn:
        after = conn.execute(text("SELECT COUNT(*) FROM ticket")).scalar()

    assert response.status_code == 404
    assert response.json()["error"] == "TrainNotFound"
    assert before == after
