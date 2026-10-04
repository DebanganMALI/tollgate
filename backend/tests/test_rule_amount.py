from decimal import Decimal

import pytest

from app.policy.config import PolicyConfig
from app.policy.models import PaymentProposal, Verdict
from app.policy.rules import check_amount

CFG = PolicyConfig()


def proposal(amount):
    return PaymentProposal(merchant_id="github", amount=amount, category="software")


@pytest.mark.parametrize("amount", ["0.01", "49.99", "50.00"])
def test_small_amounts_pass(amount):
    assert check_amount(proposal(amount), CFG) is None


@pytest.mark.parametrize("amount", ["50.01", "99.99", "100.00"])
def test_mid_amounts_need_review(amount):
    v = check_amount(proposal(amount), CFG)
    assert v.severity is Verdict.REVIEW
    assert v.rule == "amount_review"


@pytest.mark.parametrize("amount", ["100.01", "5000"])
def test_large_amounts_denied(amount):
    v = check_amount(proposal(amount), CFG)
    assert v.severity is Verdict.DENY
    assert v.rule == "amount_limit"


def test_respects_custom_config():
    cfg = PolicyConfig(max_per_transaction=Decimal(20), review_above=Decimal(10))
    assert check_amount(proposal("25"), cfg).severity is Verdict.DENY
