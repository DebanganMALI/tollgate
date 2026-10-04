import httpx
import pytest
from pydantic import SecretStr

from app.paypal.client import PayPalClient, PayPalError


def make_client(handler):
    http = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="https://paypal.test"
    )
    return PayPalClient("id", SecretStr("secret"), "https://paypal.test", http=http)


def ok_token(request):
    return httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})


def test_fetches_token_with_basic_auth():
    seen = []

    def handler(request):
        seen.append(request)
        return ok_token(request)

    assert make_client(handler).access_token() == "tok"
    assert seen[0].url.path == "/v1/oauth2/token"
    assert seen[0].headers["authorization"].startswith("Basic ")


def test_token_is_cached():
    calls = []

    def handler(request):
        calls.append(request)
        return ok_token(request)

    client = make_client(handler)
    client.access_token()
    client.access_token()
    assert len(calls) == 1


def test_token_failure_raises():
    client = make_client(lambda r: httpx.Response(401, json={"error": "invalid_client"}))
    with pytest.raises(PayPalError):
        client.access_token()
