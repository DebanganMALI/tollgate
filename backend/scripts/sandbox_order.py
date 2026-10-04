import uuid
from decimal import Decimal

from app.config import get_settings
from app.paypal.client import PayPalClient


def main() -> None:
    s = get_settings()
    client = PayPalClient(s.paypal_client_id, s.paypal_client_secret, s.paypal_base_url)
    order = client.create_order(Decimal("1.00"), "USD", "tollgate-smoke", str(uuid.uuid4()))
    approve = next(
        (link["href"] for link in order.get("links", []) if link["rel"] == "approve"),
        None,
    )
    print(f"Order {order['id']} status={order['status']}")
    print(f"Approve URL: {approve}")


if __name__ == "__main__":
    main()
