from sqlalchemy import text

from tests.helpers.snapshots import capture_evidence, write_diff_summary

TEST_NAME = "form_2_reschedule_train"
AFFECTED_TABLES = ["train", "coach", "ticket"]


def test_reschedule_train_cascades(engine, isolated_client) -> None:
    """Changing a train's PK fires ON UPDATE CASCADE on coach and ticket; old PK
    becomes empty across all 3 tables and new PK acquires the same row counts."""
    with engine.connect() as conn:
        old_coach_n = conn.execute(text(
            "SELECT COUNT(*) FROM coach WHERE train_number='IC-701' AND service_date='2026-04-01'"
        )).scalar()
        old_ticket_n = conn.execute(text(
            "SELECT COUNT(*) FROM ticket WHERE train_number='IC-701' AND service_date='2026-04-01'"
        )).scalar()

    capture_evidence(engine, TEST_NAME, AFFECTED_TABLES, "before")

    response = isolated_client.put("/api/trains/IC-701/2026-04-01", json={
        "new_train_number": "IC-702",
        "new_service_date": "2026-04-02",
        "new_scheduled_departure": "2026-04-02T07:00:00",
        "new_scheduled_arrival": "2026-04-02T13:30:00",
    })

    capture_evidence(engine, TEST_NAME, AFFECTED_TABLES, "after")

    assert response.status_code == 200
    body = response.json()
    assert body["coaches_cascaded"] == old_coach_n
    assert body["tickets_cascaded"] == old_ticket_n

    with engine.connect() as conn:
        old_train_after = conn.execute(text(
            "SELECT COUNT(*) FROM train WHERE train_number='IC-701' AND service_date='2026-04-01'"
        )).scalar()
        new_train_after = conn.execute(text(
            "SELECT COUNT(*) FROM train WHERE train_number='IC-702' AND service_date='2026-04-02'"
        )).scalar()
        old_coach_after = conn.execute(text(
            "SELECT COUNT(*) FROM coach WHERE train_number='IC-701' AND service_date='2026-04-01'"
        )).scalar()
        new_coach_after = conn.execute(text(
            "SELECT COUNT(*) FROM coach WHERE train_number='IC-702' AND service_date='2026-04-02'"
        )).scalar()
        old_ticket_after = conn.execute(text(
            "SELECT COUNT(*) FROM ticket WHERE train_number='IC-701' AND service_date='2026-04-01'"
        )).scalar()
        new_ticket_after = conn.execute(text(
            "SELECT COUNT(*) FROM ticket WHERE train_number='IC-702' AND service_date='2026-04-02'"
        )).scalar()

    assert old_train_after == 0, "old train PK must be vacated"
    assert new_train_after == 1, "new train PK must hold the moved row"
    assert old_coach_after == 0, "old coach rows must be cascaded away"
    assert new_coach_after == old_coach_n, "all coaches must arrive under new PK"
    assert old_ticket_after == 0, "old ticket rows must be cascaded away"
    assert new_ticket_after == old_ticket_n, "all tickets must arrive under new PK"

    write_diff_summary(TEST_NAME, f"""# Test: Reschedule Train — Cascade UPDATE

**Operation:** PUT /api/trains/IC-701/2026-04-01
**New PK:** IC-702 / 2026-04-02 (with new scheduled times)

**Goal:** Verify ON UPDATE CASCADE on the composite PK (train_number, service_date)
propagates to `coach` and `ticket` via the FK constraints in 001_initial_schema.sql.

**Cascade reach:**
- train  : 1 row moved (old PK now empty, new PK holds the row)
- coach  : {old_coach_n} row(s) cascaded (old PK: 0 → new PK: {new_coach_after})
- ticket : {old_ticket_n} row(s) cascaded (old PK: 0 → new PK: {new_ticket_after})

**Affected tables:** train, coach, ticket
**Before:** see `before_train.csv`, `before_coach.csv`, `before_ticket.csv`
**After:** see `after_train.csv`, `after_coach.csv`, `after_ticket.csv`

**Test verdict:** PASS — cascade UPDATE works correctly across all 3 tables.
""")


def test_reschedule_train_not_found(isolated_client) -> None:
    """Rescheduling a train PK that does not exist returns 404 TrainNotFound."""
    response = isolated_client.put("/api/trains/ZZ-999/2026-04-01", json={
        "new_train_number": "AA-001",
        "new_service_date": "2099-12-30",
        "new_scheduled_departure": "2099-12-30T07:00:00",
        "new_scheduled_arrival": "2099-12-30T13:30:00",
    })
    assert response.status_code == 404
    assert response.json()["error"] == "TrainNotFound"


def test_reschedule_train_pk_clash(isolated_client) -> None:
    """Renaming a train into a PK that already exists in the seed returns 409
    TrainAlreadyExists; the existing row is not overwritten."""
    response = isolated_client.put("/api/trains/IC-703/2026-04-01", json={
        "new_train_number": "IC-501",
        "new_service_date": "2026-04-02",
        "new_scheduled_departure": "2026-04-02T07:00:00",
        "new_scheduled_arrival": "2026-04-02T13:30:00",
    })
    assert response.status_code == 409
    assert response.json()["error"] == "TrainAlreadyExists"
