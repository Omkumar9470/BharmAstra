import json
import math
from fastapi.responses import Response


def sanitize_nan(obj):
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