def test_thank_you_never_mentions_cash_amount(client):
    # Test generation for cash gift
    res = client.post("/api/thank-you/generate", json={
        "guest_id": 1,
        "gift_id": 2,  # Cash envelope gift
        "tone": "warm"
    })
    assert res.status_code == 200
    data = res.json()
    msg = data["message_text"]

    # Verify strict rule: cash amounts or numeric currency values must NEVER be in message
    assert "Tk" not in msg
    assert "BDT" not in msg
    assert "taka" not in msg.lower()
    assert "amount" not in msg.lower()
    assert "thoughtful gift" in msg or "kind blessings" in msg

def test_thank_you_mark_sent_tracks_history(client):
    # Find a pending message
    res = client.get("/api/thank-you?status=pending")
    assert res.status_code == 200
    items = res.json()["items"]
    if items:
        msg_id = items[0]["id"]
        mark_res = client.post(f"/api/thank-you/{msg_id}/mark-sent?sent_via=WhatsApp")
        assert mark_res.status_code == 200
        updated = mark_res.json()
        assert updated["status"] == "sent"
        assert updated["sent_via"] == "WhatsApp"
        assert len(updated["status_history"]) >= 1
