def test_list_gifts(client):
    response = client.get("/api/gifts")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 4

    # Verify original handwritten note preservation
    notes = [g["original_note"] for g in data["items"]]
    assert any("Rahman uncle - dinner set" in n for n in notes)
    assert any("Shilpi khala + family, envelope" in n for n in notes)
    assert any("big box, no card???" in n for n in notes)

def test_joint_gift_and_optional_cash(client):
    # Retrieve Shilpi Khala gift
    response = client.get("/api/gifts?search=Shilpi")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1

    shilpi_gift = data["items"][0]
    # Check joint contributors
    assert len(shilpi_gift["contributors"]) >= 2
    # Check cash is True, but cash amount is optional/None (never guessed!)
    assert shilpi_gift["is_cash"] is True
    assert shilpi_gift["cash_amount"] is None or shilpi_gift["cash_amount"] == 0

def test_create_gift_with_unclear_note_flags_review(client):
    payload = {
        "event_id": 1,
        "gift_name": "Unclear Parcel",
        "gift_category": "Unknown",
        "quantity": 1,
        "is_cash": False,
        "original_note": "mystery bag, no card???",
        "review_status": "confirmed"  # should be auto-flagged to requires_review
    }
    response = client.post("/api/gifts", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["review_status"] == "requires_review"
    assert created["original_note"] == "mystery bag, no card???"
