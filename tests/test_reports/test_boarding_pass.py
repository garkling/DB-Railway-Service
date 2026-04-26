from decimal import Decimal


def test_boarding_pass_returns_full_payload(isolated_client) -> None:
    """Boarding pass for IC-701 / 2026-04-01 / ticket #1 returns the fully-composed
    payload with operator name, passenger full name, class name, origin/destination,
    and the seeded price 675.00 (UZ/1ST/route 1 from operator_class_route_pricing)."""
    response = isolated_client.get("/api/reports/boarding-pass", params={
        "train": "IC-701",
        "date": "2026-04-01",
        "ticket": 1,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["operator_name"] == "Ukrzaliznytsia"
    assert data["origin_station"] == "Lviv"
    assert data["destination_station"] == "Kyiv-Pasazhyrskyi"
    assert data["passenger_full_name"] == "Oleksandr Kovalenko"
    assert data["class_name"] == "First Class"
    assert Decimal(data["price_paid"]) == Decimal("675.00")
    assert data["ticket_number"] == 1


def test_boarding_pass_ticket_not_found(isolated_client) -> None:
    """Boarding pass for a non-existent ticket number returns 404 TicketNotFound."""
    response = isolated_client.get("/api/reports/boarding-pass", params={
        "train": "IC-701",
        "date": "2026-04-01",
        "ticket": 999,
    })
    assert response.status_code == 404
    assert response.json()["error"] == "TicketNotFound"
