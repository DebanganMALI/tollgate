import pytest

from app.policy.config import PolicyConfig
from app.policy.models import PaymentProposal, Verdict
from app.policy.rules import check_currency

CFG = PolicyConfig()


def proposal(currency):
    return PaymentProposal(
        merchant_id="github", amount="99", category="software", currency=currency
    )


def test_usd_passes():
    assert check_currency(proposal("USD"), CFG) is None


@pytest.mark.parametrize("currency", ["KWD", "BTC", "XAU", "EUR"])
def test_other_currencies_denied(currency):
    v = check_currency(proposal(currency), CFG)
    assert v.severity is Verdict.DENY
    assert v.rule == "currency_not_allowed"
