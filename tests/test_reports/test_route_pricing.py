def test_route_pricing_unfiltered_returns_all(isolated_client) -> None:
    """Unfiltered pricing schedule returns all 10 seeded rows; every row has
    operator_name / class_name / route_name populated by the enrichment join."""
    response = isolated_client.get("/api/reports/route-pricing")
    assert response.status_code == 200
    data = response.json()
    assert len(data["rows"]) == 10
    for row in data["rows"]:
        assert row["operator_name"], "operator_name must be enriched"
        assert row["class_name"], "class_name must be enriched"
        assert row["route_name"], "route_name must be enriched"
    assert data["operator_filter"] is None
    assert data["route_filter"] is None


def test_route_pricing_filtered_by_operator(isolated_client) -> None:
    """Filtering by operator=UZ returns the 6 UZ pricing rows (1ST/2ND/SLP × routes 1/2);
    every returned row has operator_code == "UZ"."""
    response = isolated_client.get(
        "/api/reports/route-pricing", params={"operator": "UZ"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["rows"]) == 6
    for row in data["rows"]:
        assert row["operator_code"] == "UZ"
    assert data["operator_filter"] == "UZ"


def test_route_pricing_empty_filter_combination(isolated_client) -> None:
    """A filter combination with zero matching rows (PKP doesn't price route 1)
    returns 200 with rows=[] — NOT a 404. Empty results are valid."""
    response = isolated_client.get(
        "/api/reports/route-pricing",
        params={"operator": "PKP", "route": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rows"] == []
    assert data["operator_filter"] == "PKP"
    assert data["route_filter"] == 1
