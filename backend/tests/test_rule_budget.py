from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.policy.config import PolicyConfig
from app.policy.history import SpendHistory
from app.policy.models import PaymentProposal, Verdict
from app.policy.rules import check_daily_budget

CFG = PolicyConfig()
NOW = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)


def proposal(amount):
    return PaymentProposal(merchant_id="github", amount=amount, category="software")


def history(*items):
    h = SpendHistory()
    for amount, hours_ago in items:
        h.add(Decimal(amount), NOW - timedelta(hours=hours_ago))
    return h


def test_empty_history_passes():
    assert check_daily_budget(proposal("100"), CFG, history(), NOW) is None


def test_exactly_reaching_budget_passes():
    assert check_daily_budget(proposal("50"), CFG, history((250, 1)), NOW) is None


def test_exceeding_budget_denied():
    v = check_daily_budget(proposal("50.01"), CFG, history((250, 1)), NOW)
    assert v.severity is Verdict.DENY
    assert v.rule == "daily_budget"


def test_old_spend_outside_window_ignored():
    assert check_daily_budget(proposal("50"), CFG, history((290, 25)), NOW) is None
