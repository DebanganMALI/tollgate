from datetime import datetime, timedelta

from app.policy.config import PolicyConfig
from app.policy.history import SpendHistory
from app.policy.models import PaymentProposal, Verdict, Violation


def check_amount(p: PaymentProposal, cfg: PolicyConfig) -> Violation | None:
    if p.amount > cfg.max_per_transaction:
        return Violation(
            rule="amount_limit",
            message=f"{p.amount} exceeds limit {cfg.max_per_transaction}",
        )
    if p.amount > cfg.review_above:
        return Violation(
            rule="amount_review",
            message=f"{p.amount} is above review threshold {cfg.review_above}",
            severity=Verdict.REVIEW,
        )
    return None


def check_merchant(p: PaymentProposal, cfg: PolicyConfig) -> Violation | None:
    merchant = p.merchant_id.strip().casefold()
    allowed = {m.casefold() for m in cfg.allowed_merchants}
    if merchant not in allowed:
        return Violation(
            rule="merchant_not_allowed",
            message=f"Merchant '{p.merchant_id}' is not on the allow-list",
        )
    return None


def check_category(p: PaymentProposal, cfg: PolicyConfig) -> Violation | None:
    if p.category in cfg.blocked_categories:
        return Violation(
            rule="category_blocked",
            message=f"Category '{p.category}' is blocked",
        )
    return None


def check_daily_budget(
    p: PaymentProposal, cfg: PolicyConfig, history: SpendHistory, now: datetime
) -> Violation | None:
    spent = history.total_since(now - timedelta(days=1))
    if spent + p.amount > cfg.daily_budget:
        return Violation(
            rule="daily_budget",
            message=f"{spent} spent in 24h; {p.amount} would exceed {cfg.daily_budget}",
        )
    return None


def check_velocity(
    p: PaymentProposal, cfg: PolicyConfig, history: SpendHistory, now: datetime
) -> Violation | None:
    recent = history.count_since(now - timedelta(seconds=cfg.window_seconds))
    if recent + 1 > cfg.max_tx_per_window:
        return Violation(
            rule="velocity",
            message=f"{recent} payments in {cfg.window_seconds}s; limit {cfg.max_tx_per_window}",
        )
    return None
