from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field


class Category(StrEnum):
    SOFTWARE = "software"
    CLOUD = "cloud"
    OFFICE = "office"
    TRAVEL = "travel"
    OTHER = "other"


class PaymentProposal(BaseModel):
    merchant_id: str = Field(min_length=1, max_length=64)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    category: Category
    # Untrusted agent text; never used in policy decisions.
    reason: str = Field(default="", max_length=500)


class Verdict(StrEnum):
    ALLOW = "allow"
    REVIEW = "review"
    DENY = "deny"


_SEVERITY = {Verdict.ALLOW: 0, Verdict.REVIEW: 1, Verdict.DENY: 2}


class Violation(BaseModel):
    rule: str
    message: str
    severity: Verdict = Verdict.DENY


class Decision(BaseModel):
    verdict: Verdict
    violations: list[Violation] = Field(default_factory=list)

    @classmethod
    def from_violations(cls, violations: list[Violation]) -> Self:
        verdict = max(
            (v.severity for v in violations),
            key=_SEVERITY.__getitem__,
            default=Verdict.ALLOW,
        )
        return cls(verdict=verdict, violations=violations)
