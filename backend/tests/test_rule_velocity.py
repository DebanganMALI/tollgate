from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.policy.config import PolicyConfig
from app.policy.history import SpendHistory
from app.policy.models import PaymentProposal, Verdict
from app.policy.rules import check_velocity

CFG = PolicyConfig()
NOW = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)
P = PaymentProposal(merchant_id="github", amount="5", category="software")


def history(count, seconds_ago=10):
    h = SpendHistory()
    for _ in range(count):
        h.add(Decimal(1), NOW - timedelta(seconds=seconds_ago))
    return h


def test_under_limit_passes():
    assert check_velocity(P, CFG, history(4), NOW) is None


def test_burst_denied():
    v = check_velocity(P, CFG, history(5), NOW)
    assert v.severity is Verdict.DENY
    assert v.rule == "velocity"


def test_old_payments_outside_window_ignored():
    assert check_velocity(P, CFG, history(10, seconds_ago=120), NOW) is None


def test_custom_window():
    cfg = PolicyConfig(max_tx_per_window=1, window_seconds=300)
    assert check_velocity(P, cfg, history(1, seconds_ago=200), NOW).rule == "velocity"
