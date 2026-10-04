import json
from decimal import Decimal

import httpx
import pytest
from pydantic import SecretStr

from app.paypal.client import PayPalClient, PayPalError


def make_client(order_status=201, seen=None):
    def handler(request):
        if request.url.path == "/v1/oauth2/token":
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
        if seen is not None:
            seen.append(request)
        return httpx.Response(order_status, json={"id": "ORDER123", "status": "CREATED"})

    http = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://paypal.test"
    )
    return PayPalClient("id", SecretStr("secret"), "https://paypal.test", http=http)


def test_create_order_returns_order():
    order = make_client().create_order(Decimal("19.99"), "USD", "ref-1", "req-1")
    assert order == {"id": "ORDER123", "status": "CREATED"}


def test_create_order_sends_amount_and_idempotency_key():
    seen = []
    make_client(seen=seen).create_order(Decimal(5), "USD", "ref-1", "req-42")
    req = seen[0]
    body = json.loads(req.content)
    assert req.headers["paypal-request-id"] == "req-42"
    assert req.headers["authorization"] == "Bearer tok"
    assert body["purchase_units"][0]["amount"] == {"currency_code": "USD", "value": "5.00"}


def test_create_order_failure_raises():
    with pytest.raises(PayPalError):
        make_client(order_status=422).create_order(Decimal(1), "USD", "r", "q")
