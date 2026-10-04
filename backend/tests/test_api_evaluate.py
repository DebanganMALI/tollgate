from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def post(**overrides):
    body = {"merchant_id": "github", "amount": "20", "category": "software"}
    body.update(overrides)
    return client.post("/policy/evaluate", json=body)


def test_allowed_payment():
    r = post()
    assert r.status_code == 200
    assert r.json()["verdict"] == "allow"


def test_denied_payment_lists_violations():
    body = post(merchant_id="evil", category="travel").json()
    assert body["verdict"] == "deny"
    assert len(body["violations"]) == 2


def test_invalid_payload_rejected():
    assert post(amount="-1").status_code == 422


def test_override_field_rejected():
    assert post(verdict="allow").status_code == 422
