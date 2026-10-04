import pytest

from app.policy.config import PolicyConfig
from app.policy.models import Category, PaymentProposal, Verdict
from app.policy.rules import check_category

CFG = PolicyConfig()


def proposal(category):
    return PaymentProposal(merchant_id="github", amount="10", category=category)


def test_travel_blocked_by_default():
    v = check_category(proposal("travel"), CFG)
    assert v.severity is Verdict.DENY
    assert v.rule == "category_blocked"


@pytest.mark.parametrize("category", ["software", "cloud", "office", "other"])
def test_other_categories_pass(category):
    assert check_category(proposal(category), CFG) is None


def test_custom_blocked_category():
    cfg = PolicyConfig(blocked_categories=frozenset({Category.OTHER}))
    assert check_category(proposal("other"), cfg).rule == "category_blocked"


def test_empty_block_list_allows_everything():
    cfg = PolicyConfig(blocked_categories=frozenset())
    assert check_category(proposal("travel"), cfg) is None
