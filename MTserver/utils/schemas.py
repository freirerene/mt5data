from pydantic import BaseModel
from typing import Optional


class GetHistory(BaseModel):
    symbol: str
    timeframe: str
    ticks: Optional[int] = 0
    from_date: Optional[str] = ""


class TradeRequest(BaseModel):
    symbol: str
    volume: float
    deviation: float
    magic: Optional[int] = 100
    comment: Optional[str] = "FastAPI order"
