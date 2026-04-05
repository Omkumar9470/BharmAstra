# routers/technical.py
from fastapi import APIRouter, Query
from services.stock_data import resolve_ticker, fetch_ohlcv, fetch_stock_info
from utils.cache import get_cached, set_cache
from services.technical import compute_indicators, generate_signals


router = APIRouter()

@router.get("/stock/search")
def search_ticker(q: str = Query(..., description="Company name or ticker")):
    """Resolve a company name to a ticker symbol."""
    ticker = resolve_ticker(q)
    return {"query": q, "resolved_ticker": ticker}


@router.get("/stock/{ticker}/info")
def stock_info(ticker: str):
    """Get stock metadata."""
    cache_key = f"info:{ticker}"
    cached = get_cached(cache_key)
    if cached:
        return {**cached, "source": "cache"}
    
    data = fetch_stock_info(ticker)
    if "error" not in data:
        set_cache(cache_key, data)
    return {**data, "source": "live"}


@router.get("/stock/{ticker}/ohlcv")
def stock_ohlcv(
    ticker: str,
    period: str = Query("6mo", description="1mo | 3mo | 6mo | 1y | 2y"),
    interval: str = Query("1d", description="1d | 1wk | 1mo")
):
    """Get OHLCV price history."""
    cache_key = f"ohlcv:{ticker}:{period}:{interval}"
    cached = get_cached(cache_key)
    if cached:
        return {**cached, "source": "cache"}
    
    data = fetch_ohlcv(ticker, period, interval)
    if "error" not in data:
        set_cache(cache_key, data)
    return {**data, "source": "live"}

@router.get("/stock/{ticker}/indicators")
def stock_indicators(
    ticker: str,
    period: str = Query("6mo", description="1mo | 3mo | 6mo | 1y")
):
    """Get full indicator history for charting."""
    cache_key = f"indicators:{ticker}:{period}"
    cached = get_cached(cache_key)
    if cached:
        return {**cached, "source": "cache"}
    
    data = compute_indicators(ticker, period)
    if "error" not in data:
        set_cache(cache_key, data)
    return {**data, "source": "live"}

@router.get("/stock/{ticker}/signals")
def stock_signals(ticker: str):
    """Get latest technical signals + bullish/bearish score."""
    cache_key = f"signals:{ticker}"
    cached = get_cached(cache_key)
    if cached:
        return {**cached, "source": "cache"}

    data = generate_signals(ticker)
    if "error" not in data:
        set_cache(cache_key, data)
    return {**data, "source": "live"}