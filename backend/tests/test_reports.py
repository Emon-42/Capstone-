def test_dashboard_stats(client):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_guests"] >= 5
    assert data["total_gift_records"] >= 5
    assert data["unidentified_gifts"] >= 1
    assert data["gifts_requiring_review"] >= 1
    assert "completion_rate_percentage" in data

def test_export_csv_endpoints(client):
    for export_type in ["guests", "gifts", "thank_you", "history"]:
        res = client.get(f"/api/reports/export/csv?type={export_type}")
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert len(res.text) > 0
