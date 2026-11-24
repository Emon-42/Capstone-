def test_list_guests(client):
    response = client.get("/api/guests")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    assert any(g["full_name"] == "Rahman Uncle" for g in data["items"])

def test_create_and_delete_unknown_guest(client):
    # Test support for unidentified guest
    guest_payload = {
        "full_name": "Unidentified Chittagong Relatives",
        "relationship_type": "Unknown",
        "family_group": "Chittagong Family",
        "is_unidentified": True,
        "notes": "Didn't catch individual names during dinner rush"
    }
    create_res = client.post("/api/guests", json=guest_payload)
    assert create_res.status_code == 201
    guest_data = create_res.json()
    assert guest_data["is_unidentified"] is True
    guest_id = guest_data["id"]

    # Delete (soft delete)
    del_res = client.delete(f"/api/guests/{guest_id}")
    assert del_res.status_code == 200

    # Ensure soft deleted
    get_res = client.get(f"/api/guests/{guest_id}")
    assert get_res.status_code == 404
