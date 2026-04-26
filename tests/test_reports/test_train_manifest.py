from decimal import Decimal


def test_train_manifest_returns_all_passengers(isolated_client) -> None:
    """Manifest for IC-701 / 2026-04-01 lists exactly the 4 ticketed passengers
    (P001..P004), rows are sorted ascending by ticket_number, and joined fields
    (class_name, price_paid) are populated by the bulk-fetch enrichment step."""
    response = isolated_client.get("/api/reports/train-manifest", params={
        "train": "IC-701",
        "date": "2026-04-01",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["train_number"] == "IC-701"
    assert data["service_date"] == "2026-04-01"
    assert data["total_passengers"] == 4

    pids = {row["passenger_id"] for row in data["rows"]}
    assert pids == {"P001", "P002", "P003", "P004"}

    ticket_numbers = [row["ticket_number"] for row in data["rows"]]
    assert ticket_numbers == sorted(ticket_numbers), "rows must be sorted by ticket_number"

    p001 = next(r for r in data["rows"] if r["passenger_id"] == "P001")
    assert p001["class_name"] == "First Class"
    assert Decimal(p001["price_paid"]) == Decimal("675.00")


def test_train_manifest_empty_for_unticketed_train(isolated_client) -> None:
    """Manifest for IC-705 / 2026-04-03 (no tickets in seed) returns 200 with
    total_passengers=0 and rows=[]; header metadata is still populated."""
    response = isolated_client.get("/api/reports/train-manifest", params={
        "train": "IC-705",
        "date": "2026-04-03",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total_passengers"] == 0
    assert data["rows"] == []
    assert data["operator_name"] == "Ukrzaliznytsia"
    assert data["route_name"] == "Lviv-Kyiv"


def test_train_manifest_train_not_found(isolated_client) -> None:
    """Manifest for a non-existent train PK returns 404 TrainNotFound."""
    response = isolated_client.get("/api/reports/train-manifest", params={
        "train": "ZZ-999",
        "date": "2026-04-01",
    })
    assert response.status_code == 404
    assert response.json()["error"] == "TrainNotFound"
