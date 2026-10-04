from datetime import UTC, datetime

from app.policy import rules
from app.policy.config import PolicyConfig
from app.policy.history import SpendHistory
from app.policy.models import Decision, PaymentProposal


class PolicyEngine:
    def __init__(
        self, config: PolicyConfig | None = None, history: SpendHistory | None = None
    ):
        self.config = config or PolicyConfig()
        self.history = history or SpendHistory()

    def evaluate(self, p: PaymentProposal, now: datetime | None = None) -> Decision:
        now = now or datetime.now(UTC)
        cfg = self.config
        results = [
            rules.check_amount(p, cfg),
            rules.check_merchant(p, cfg),
            rules.check_category(p, cfg),
            rules.check_daily_budget(p, cfg, self.history, now),
            rules.check_velocity(p, cfg, self.history, now),
        ]
        return Decision.from_violations([v for v in results if v])

    def record(self, p: PaymentProposal, now: datetime | None = None) -> None:
        self.history.add(p.amount, now)
