# services/finbert.py
from transformers import pipeline
import threading

# Load model once at startup — cached in memory
_model = None
_lock  = threading.Lock()


def get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                print("Loading FinBERT model... (first time only)")
                _model = pipeline(
                    "text-classification",
                    model="ProsusAI/finbert",
                    tokenizer="ProsusAI/finbert",
                    top_k=None,   # return all 3 label scores
                )
                print("FinBERT model loaded.")
    return _model


def score_text(text: str) -> dict:
    """
    Score a single piece of text.
    Returns: { positive, negative, neutral, label, confidence }
    """
    if not text or len(text.strip()) < 10:
        return _neutral_result()

    try:
        model  = get_model()
        # Truncate to 512 tokens max (FinBERT limit)
        text   = text[:1000]
        result = model(text)[0]  # list of {label, score}

        scores = {r["label"].lower(): round(r["score"], 4) for r in result}
        positive = scores.get("positive", 0)
        negative = scores.get("negative", 0)
        neutral  = scores.get("neutral",  0)

        # Dominant label
        label = max(scores, key=scores.get)
        confidence = scores[label]

        return {
            "positive":   positive,
            "negative":   negative,
            "neutral":    neutral,
            "label":      label,
            "confidence": confidence,
        }
    except Exception as e:
        print(f"FinBERT error: {e}")
        return _neutral_result()


def _neutral_result() -> dict:
    return {
        "positive":   0.0,
        "negative":   0.0,
        "neutral":    1.0,
        "label":      "neutral",
        "confidence": 1.0,
    }