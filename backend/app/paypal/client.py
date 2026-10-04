import time
from decimal import Decimal

import httpx
from pydantic import SecretStr


class PayPalError(Exception):
    pass


class PayPalClient:
    def __init__(
        self,
        client_id: str,
        secret: SecretStr,
        base_url: str,
        http: httpx.Client | None = None,
    ):
        self._client_id = client_id
        self._secret = secret
        self._http = http or httpx.Client(base_url=base_url, timeout=15)
        self._token: str | None = None
        self._expires_at = 0.0

    def access_token(self) -> str:
        if self._token and time.monotonic() < self._expires_at:
            return self._token
        r = self._http.post(
            "/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(self._client_id, self._secret.get_secret_value()),
        )
        if r.status_code != 200:
            raise PayPalError(f"Token request failed: {r.status_code}")
        body = r.json()
        self._token = body["access_token"]
        self._expires_at = time.monotonic() + body["expires_in"] - 60
        return self._token

    def create_order(
        self, amount: Decimal, currency: str, reference_id: str, request_id: str
    ) -> dict:
        r = self._http.post(
            "/v2/checkout/orders",
            headers={
                "Authorization": f"Bearer {self.access_token()}",
                "PayPal-Request-Id": request_id,
            },
            json={
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "reference_id": reference_id,
                        "amount": {"currency_code": currency, "value": f"{amount:.2f}"},
                    }
                ],
            },
        )
        if r.status_code not in (200, 201):
            raise PayPalError(f"Create order failed: {r.status_code}")
        return r.json()
