# utils/cache.py
import os
from supabase import create_client
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

CACHE_TTL_HOURS = 6  # refresh data every 6 hours

def get_cached(key: str) -> dict | None:
    """Retrieve cached data if it exists and is not stale."""
    try:
        result = supabase.table("cache") \
            .select("*") \
            .eq("key", key) \
            .execute()
        
        if not result.data:
            return None
        
        row = result.data[0]
        cached_at = datetime.fromisoformat(row["cached_at"])
        
        # Check if cache is still fresh
        if datetime.utcnow() - cached_at > timedelta(hours=CACHE_TTL_HOURS):
            return None  # stale
        
        return json.loads(row["value"])
    except Exception:
        return None


def set_cache(key: str, value: dict) -> None:
    """Store data in Supabase cache table."""
    try:
        supabase.table("cache").upsert({
            "key": key,
            "value": json.dumps(value),
            "cached_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"Cache write failed: {e}")