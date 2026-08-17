import hmac
import hashlib
import json
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.services.dm_service import PSEUDOGRAM_API_KEY

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200
    print("Health check passed:", response.json())

def test_rules():
    response = client.post("/rules", json={"keyword": "PRICE", "dm_message": "Price list: $99.99"})
    assert response.status_code == 201
    data = response.json()
    assert data["keyword"] == "PRICE"
    assert "rule_id" in data
    print("Create rule passed:", data)

def test_stats():
    response = client.get("/stats")
    assert response.status_code == 200
    print("Stats passed:", response.json())

def test_webhook_signature():
    u_id = str(uuid.uuid4())[:8]
    payload = {
        "event_id": f"evt_sig_{u_id}",
        "event_type": "comment.created",
        "data": {
            "comment_id": f"cmt_sig_{u_id}",
            "post_id": "post_123",
            "text": "PRICE please",
            "from": {"user_id": f"usr_sig_{u_id}", "username": "testuser"}
        }
    }
    raw_body = json.dumps(payload).encode("utf-8")

    # Valid signature
    sig = hmac.new(PSEUDOGRAM_API_KEY.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    headers = {"X-PseudoGram-Signature": f"sha256={sig}", "Content-Type": "application/json"}

    res = client.post("/webhook", content=raw_body, headers=headers)
    assert res.status_code == 200
    print("Webhook valid signature passed:", res.json())

    # Invalid signature
    bad_headers = {"X-PseudoGram-Signature": "sha256=invalid", "Content-Type": "application/json"}
    res_bad = client.post("/webhook", content=raw_body, headers=bad_headers)
    assert res_bad.status_code == 401
    print("Webhook invalid signature rejected (401):", res_bad.json())

def test_comment_deleted_out_of_order():
    u_id = str(uuid.uuid4())[:8]
    cmt_id = f"cmt_del_early_{u_id}"

    # 1. comment.deleted arrives BEFORE comment.created
    del_payload = {
        "event_id": f"evt_del_{u_id}",
        "event_type": "comment.deleted",
        "data": {"comment_id": cmt_id}
    }
    res_del = client.post("/webhook", json=del_payload)
    assert res_del.status_code == 200

    # 2. comment.created arrives AFTER comment.deleted
    create_payload = {
        "event_id": f"evt_create_{u_id}",
        "event_type": "comment.created",
        "data": {
            "comment_id": cmt_id,
            "text": "PRICE list",
            "from": {"user_id": f"usr_del_{u_id}"}
        }
    }
    res_create = client.post("/webhook", json=create_payload)
    assert res_create.status_code == 200
    assert res_create.json()["message"] == "comment already deleted, skipping DM"
    print("Out-of-order comment.deleted test passed!")

if __name__ == "__main__":
    test_health()
    test_rules()
    test_stats()
    test_webhook_signature()
    test_comment_deleted_out_of_order()
