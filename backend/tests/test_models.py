from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.policy.models import Category, PaymentProposal


def make(**overrides):
    data = {"merchant_id": "github", "amount": "19.99", "category": "software"}
    data.update(overrides)
    return PaymentProposal(**data)


def test_valid_proposal():
    p = make()
    assert p.amount == Decimal("19.99")
    assert p.category is Category.SOFTWARE
    assert p.currency == "USD"


@pytest.mark.parametrize("amount", ["0", "-5", "10.999"])
def test_rejects_bad_amount(amount):
    with pytest.raises(ValidationError):
        make(amount=amount)


def test_rejects_unknown_category():
    with pytest.raises(ValidationError):
        make(category="crypto")


def test_rejects_bad_currency():
    with pytest.raises(ValidationError):
        make(currency="usd")
