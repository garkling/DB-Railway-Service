from sqlalchemy import text

from tests.helpers.snapshots import capture_evidence, write_diff_summary

TEST_NAME = "form_3_cancel_ticket"
AFFECTED_TABLES = ["ticket"]


def test_cancel_ticket_succeeds(engine, isolated_client) -> None:
    """Cancelling ticket #1 on IC-701 / 2026-04-01 removes exactly one row from
    `ticket`; all other ticket rows remain untouched and the response is 204."""
    capture_evidence(engine, TEST_NAME, AFFECTED_TABLES, "before")

    with engine.connect() as conn:
        before_total = conn.execute(text("SELECT COUNT(*) FROM ticket")).scalar()
        target_existed = conn.execute(text(
            "SELECT COUNT(*) FROM ticket WHERE train_number='IC-701' "
            "AND service_date='2026-04-01' AND ticket_number=1"
        )).scalar()

    assert target_existed == 1, "fixture sanity: ticket #1 on IC-701/2026-04-01 should exist"

    response = isolated_client.delete("/api/tickets/IC-701/2026-04-01/1")

    capture_evidence(engine, TEST_NAME, AFFECTED_TABLES, "after")

    with engine.connect() as conn:
        after_total = conn.execute(text("SELECT COUNT(*) FROM ticket")).scalar()
        target_remaining = conn.execute(text(
            "SELECT COUNT(*) FROM ticket WHERE train_number='IC-701' "
            "AND service_date='2026-04-01' AND ticket_number=1"
        )).scalar()
        sibling_remaining = conn.execute(text(
            "SELECT COUNT(*) FROM ticket WHERE train_number='IC-701' "
            "AND service_date='2026-04-01' AND ticket_number IN (2, 3, 4)"
        )).scalar()

    assert response.status_code == 204
    assert response.content == b"", "204 No Content response must have empty body"
    assert after_total == before_total - 1, "exactly one row must be removed"
    assert target_remaining == 0, "the target ticket must be gone"
    assert sibling_remaining == 3, "siblings on the same train must remain untouched"

    write_diff_summary(TEST_NAME, f"""# Test: Cancel Ticket — Success

**Operation:** DELETE /api/tickets/IC-701/2026-04-01/1
**Result:** 204 No Content (empty body).

**Row counts:**
- ticket total: {before_total} → {after_total} (−1)
- target row (IC-701/2026-04-01/#1): 1 → 0
- sibling rows on same train (IC-701/2026-04-01/#2,#3,#4): 3 → 3 (untouched)

**Affected tables:** ticket
**Before:** see `before_ticket.csv` ({before_total} rows)
**After:** see `after_ticket.csv` ({after_total} rows)

**Test verdict:** PASS — DELETE removed exactly one row, no side effects on siblings.
""")


def test_cancel_ticket_not_found(isolated_client) -> None:
    """Cancelling a ticket number that does not exist returns 404 TicketNotFound."""
    response = isolated_client.delete("/api/tickets/IC-701/2026-04-01/999")
    assert response.status_code == 404
    assert response.json()["error"] == "TicketNotFound"
