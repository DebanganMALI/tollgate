from decimal import Decimal
from enum import StrEnum

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
