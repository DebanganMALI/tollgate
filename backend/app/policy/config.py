from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.policy.models import Category


class PolicyConfig(BaseModel):
    max_per_transaction: Decimal = Field(default=Decimal("100.00"), gt=0)
    review_above: Decimal = Field(default=Decimal("50.00"), gt=0)
    daily_budget: Decimal = Field(default=Decimal("300.00"), gt=0)
    max_tx_per_window: int = Field(default=5, gt=0)
    window_seconds: int = Field(default=60, gt=0)
    allowed_currencies: frozenset[str] = frozenset({"USD"})
    allowed_merchants: frozenset[str] = frozenset(
        {"github", "render", "figma", "notion", "aws"}
    )
    blocked_categories: frozenset[Category] = frozenset({Category.TRAVEL})

    @model_validator(mode="after")
    def check_thresholds(self) -> Self:
        if self.review_above > self.max_per_transaction:
            raise ValueError("review_above must not exceed max_per_transaction")
        return self
