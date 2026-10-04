from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.policy.config import PolicyConfig
from app.policy.models import Category


def test_defaults_are_valid():
    cfg = PolicyConfig()
    assert "github" in cfg.allowed_merchants
    assert Category.TRAVEL in cfg.blocked_categories


def test_review_above_cannot_exceed_hard_limit():
    with pytest.raises(ValidationError):
        PolicyConfig(max_per_transaction=Decimal(50), review_above=Decimal(80))


def test_rejects_non_positive_budget():
    with pytest.raises(ValidationError):
        PolicyConfig(daily_budget=Decimal(0))
