# main.py
import json
import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from utils.response import sanitize_nan, SafeJSONResponse
from routers import technical, sentiment, recommendation, fundamental


def sanitize_nan(obj):
    """Recursively walk any dict/list and replace NaN/Inf with None."""
    if isinstance(obj, dict):
        return {k: sanitize_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_nan(i) for i in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj


class SafeJSONResponse(Response):
    media_type = "application/json"

    def render(self, content) -> bytes:
        clean = sanitize_nan(content)
        return json.dumps(clean, ensure_ascii=False).encode("utf-8")


app = FastAPI(title="Stock Predictor API", default_response_class=SafeJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(technical.router, prefix="/api")
app.include_router(sentiment.router, prefix="/api")
app.include_router(recommendation.router, prefix="/api")
app.include_router(fundamental.router, prefix="/api")

@app.get("/ping")
def ping():
    return {"status": "alive"}