from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.policy.history import SpendHistory

NOW = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)


def test_empty_history():
    h = SpendHistory()
    assert h.total_since(NOW) == 0
    assert h.count_since(NOW) == 0


def test_only_recent_records_count():
    h = SpendHistory()
    h.add(Decimal(40), NOW - timedelta(hours=2))
    h.add(Decimal(60), NOW - timedelta(hours=30))
    since = NOW - timedelta(days=1)
    assert h.total_since(since) == Decimal(40)
    assert h.count_since(since) == 1


def test_add_defaults_to_now():
    h = SpendHistory()
    h.add(Decimal(5))
    assert h.count_since(datetime.now(UTC) - timedelta(minutes=1)) == 1
