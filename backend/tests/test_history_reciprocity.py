def test_reciprocity_comparison(client):
    # Rahman Uncle received a dinner set and has return gift
    res = client.get("/api/gift-history/reciprocity/1")
    assert res.status_code == 200
    data = res.json()
    assert "gifts_received" in data
    assert "gifts_given_in_return" in data
    assert len(data["gifts_received"]) >= 1

def test_record_return_gift(client):
    payload = {
        "guest_id": 2,
        "event_name": "Shilpi Khala's Daughter's Wedding",
        "event_type": "given_return",
        "gift_description": "Microwave Oven and Crockery Set",
        "category": "Household Items",
        "event_date": "2027-05-10",
        "notes": "Reciprocal gift from Farhana's family"
    }
    res = client.post("/api/gift-history", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["event_type"] == "given_return"
    assert "Shilpi" in created["event_name"]
