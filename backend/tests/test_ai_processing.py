def test_ai_process_note_rahman_uncle(client):
    payload = {"note_text": "Rahman uncle - dinner set"}
    res = client.post("/api/ai/process-note", json=payload)
    assert res.status_code == 200
    data = res.json()["extracted_data"]
    assert any("Rahman" in name for name in data["possible_guest_names"])
    assert "Dinner Set" in data["gift_name"]
    assert data["gift_category"] == "Household Items"
    assert data["is_cash"] is False

def test_ai_process_note_shilpi_khala_cash_envelope(client):
    payload = {"note_text": "Shilpi khala + family, envelope"}
    res = client.post("/api/ai/process-note", json=payload)
    assert res.status_code == 200
    data = res.json()["extracted_data"]
    assert data["is_joint_gift"] is True
    assert data["is_cash"] is True
    # Crucial rule: Cash amount must NEVER be invented!
    assert data["cash_amount"] is None
    assert "cash_amount" in data["uncertain_fields"]

def test_ai_process_note_chittagong_unidentified(client):
    payload = {"note_text": "the people from Chittagong - 2 sarees, didn't catch name"}
    res = client.post("/api/ai/process-note", json=payload)
    assert res.status_code == 200
    data = res.json()["extracted_data"]
    assert data["quantity"] == 2
    assert "Clothing" in data["gift_category"]
    assert "guest_name" in data["missing_fields"]
    assert data["suggested_action"] == "review"

def test_ai_process_note_big_box_no_card(client):
    payload = {"note_text": "big box, no card???"}
    res = client.post("/api/ai/process-note", json=payload)
    assert res.status_code == 200
    data = res.json()["extracted_data"]
    assert "guest_name" in data["missing_fields"]
    assert data["suggested_action"] == "review"
