# routers/recommendation.py
from fastapi import APIRouter, Query
from services.recommendation import generate_full_recommendation
from utils.cache import get_cached, set_cache

router = APIRouter()

@router.get("/stock/{ticker}/recommend")
def recommend(
    ticker: str,
    company: str = Query(None, description="Company name override")
):
    """
    Full recommendation — runs technical + sentiment + Gemini.
    Cache TTL is 6 hours (set in utils/cache.py).
    """
    cache_key = f"recommend:{ticker}"
    cached = get_cached(cache_key)
    if cached:
        return {**cached, "source": "cache"}

    data = generate_full_recommendation(ticker, company)
    if "error" not in data:
        set_cache(cache_key, data)
    return {**data, "source": "live"}