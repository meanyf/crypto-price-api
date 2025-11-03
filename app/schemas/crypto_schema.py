from datetime import datetime
from pydantic import BaseModel


class CryptoResponse(BaseModel):
    name: str
    symbol: str
    current_price: float
    last_updated: datetime
    model_config = {"from_attributes": True}


class PriceHistoryResponse(BaseModel):
    price: float
    timestamp: datetime
    model_config = {"from_attributes": True}
