from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal


@dataclass(frozen=True)
class SpendRecord:
    amount: Decimal
    at: datetime


@dataclass
class SpendHistory:
    records: list[SpendRecord] = field(default_factory=list)

    def add(self, amount: Decimal, at: datetime | None = None) -> None:
        self.records.append(SpendRecord(amount, at or datetime.now(UTC)))

    def total_since(self, since: datetime) -> Decimal:
        return sum((r.amount for r in self.records if r.at >= since), Decimal(0))

    def count_since(self, since: datetime) -> int:
        return sum(1 for r in self.records if r.at >= since)
