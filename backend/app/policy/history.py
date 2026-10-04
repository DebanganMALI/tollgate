import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal


@dataclass(frozen=True)
class SpendRecord:
    amount: Decimal
    at: datetime
    id: str = field(default_factory=lambda: uuid.uuid4().hex)


@dataclass
class SpendHistory:
    records: list[SpendRecord] = field(default_factory=list)

    def add(self, amount: Decimal, at: datetime | None = None) -> str:
        record = SpendRecord(amount, at or datetime.now(UTC))
        self.records.append(record)
        return record.id

    def remove(self, record_id: str) -> bool:
        for i, r in enumerate(self.records):
            if r.id == record_id:
                del self.records[i]
                return True
        return False

    def total_since(self, since: datetime) -> Decimal:
        return sum((r.amount for r in self.records if r.at >= since), Decimal(0))

    def count_since(self, since: datetime) -> int:
        return sum(1 for r in self.records if r.at >= since)
