from utils.schemas import GetHistory
from utils.mtfunctions import get_history

from fastapi import APIRouter
from typing import Optional

router = APIRouter()


@router.get("/history")
async def buy_order(
    symbol: str, timeframe: str, ticks: Optional[int] = 0, from_date: Optional[str] = ""
):
    info_request = GetHistory(
        symbol=symbol, timeframe=timeframe, ticks=ticks, from_date=from_date
    )
    df = get_history(info_request)
    return df.to_dict(orient="records")
