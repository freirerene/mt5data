from utils.schemas import GetHistory
from utils.mtfunctions import get_history

from fastapi import APIRouter

router = APIRouter()


@router.post("/history")
async def buy_order(info_request: GetHistory):

    df = get_history(info_request)
    return df.to_dict(orient="records")
