# routers/sentiment.py
from fastapi import APIRouter, Query
from services.sentiment import analyze_sentiment
from services.stock_data import resolve_ticker, fetch_stock_info
from utils.cache import get_cached, set_cache

router = APIRouter()

@router.get("/stock/{ticker}/sentiment")
def stock_sentiment(
    ticker: str,
    company: str = Query(None, description="Company name override (e.g. 'Reliance Industries')")
):
    """Run sentiment analysis on news for this stock."""
    cache_key = f"sentiment:{ticker}"
    cached = get_cached(cache_key)
    if cached:
        return {**cached, "source": "cache"}

    # Resolve company name for news search
    if not company:
        info = fetch_stock_info(ticker)
        company = info.get("name", ticker.replace(".NS", "").replace(".BO", ""))

    data = analyze_sentiment(company, ticker)
    if "error" not in data:
        set_cache(cache_key, data)
    return {**data, "source": "live"}