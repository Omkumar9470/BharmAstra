"""
BharmAstra — routers/fundamental.py
Exposes GET /api/stock/{ticker}/fundamentals
"""

from fastapi import APIRouter
from utils.response import SafeJSONResponse
from services.fundamental import get_fundamental_score

router = APIRouter()


@router.get("/stock/{ticker}/fundamentals")
async def fundamentals(ticker: str):
    ticker = ticker.upper()
    data = get_fundamental_score(ticker)
    return SafeJSONResponse(content=data)