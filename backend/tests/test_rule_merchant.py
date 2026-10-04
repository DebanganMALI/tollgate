import pytest

from app.policy.config import PolicyConfig
from app.policy.models import PaymentProposal, Verdict
from app.policy.rules import check_merchant

CFG = PolicyConfig()


def proposal(merchant):
    return PaymentProposal(merchant_id=merchant, amount="10", category="software")


@pytest.mark.parametrize("merchant", ["github", "GitHub", "  github  ", "AWS"])
def test_allowed_merchants_pass(merchant):
    assert check_merchant(proposal(merchant), CFG) is None


@pytest.mark.parametrize(
    "merchant",
    ["evil-shop", "github.evil.com", "git hub", "g\u0456thub"],
)
def test_unknown_or_lookalike_merchants_denied(merchant):
    v = check_merchant(proposal(merchant), CFG)
    assert v.severity is Verdict.DENY
    assert v.rule == "merchant_not_allowed"
