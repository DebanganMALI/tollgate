from datetime import UTC, datetime

from app.policy.engine import PolicyEngine
from app.policy.models import PaymentProposal, Verdict

NOW = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)


def proposal(**overrides):
    data = {"merchant_id": "github", "amount": "20", "category": "software"}
    data.update(overrides)
    return PaymentProposal(**data)


def test_clean_proposal_allowed():
    d = PolicyEngine().evaluate(proposal(), NOW)
    assert d.verdict is Verdict.ALLOW
    assert d.violations == []


def test_mid_amount_needs_review():
    assert PolicyEngine().evaluate(proposal(amount="75"), NOW).verdict is Verdict.REVIEW


def test_all_violations_reported():
    d = PolicyEngine().evaluate(proposal(merchant_id="evil", category="travel"), NOW)
    assert d.verdict is Verdict.DENY
    assert {v.rule for v in d.violations} == {"merchant_not_allowed", "category_blocked"}


def test_deny_beats_review():
    d = PolicyEngine().evaluate(proposal(amount="75", merchant_id="evil"), NOW)
    assert d.verdict is Verdict.DENY


def test_evaluate_does_not_record_spend():
    engine = PolicyEngine()
    engine.evaluate(proposal(), NOW)
    assert engine.history.records == []


def test_recorded_spend_counts_toward_budget():
    engine = PolicyEngine()
    for _ in range(3):
        engine.record(proposal(amount="100"), NOW)
    d = engine.evaluate(proposal(amount="1"), NOW)
    assert "daily_budget" in {v.rule for v in d.violations}
