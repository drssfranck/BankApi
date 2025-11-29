from pydantic import BaseModel, Field
from typing import Literal

class CardData(BaseModel):
    id: int
    client_id: int
    card_brand: Literal["Visa", "MasterCard", "Amex", "Discover"]
    card_type: Literal["debit", "credit"]
    card_number: str = Field(..., min_length=15, max_length=16)
    expire: str = Field(..., pattern=r"^(0[1-9]|1[0-2])/\d{4}$")
    cvv: int = Field(..., ge=100, le=9999)
    has_ship: bool
    num_card_issueds: int
    credit_limit: float


