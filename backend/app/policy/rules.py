from app.policy.config import PolicyConfig
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
