# services/recommendation.py
from services.technical import generate_signals
from services.sentiment import analyze_sentiment
from services.fundamental import get_fundamental_score
from services.gemini import get_recommendation
from services.stock_data import fetch_stock_info


def generate_full_recommendation(ticker: str, company_name: str = None) -> dict:
    """
    Master function — runs all 4 engines and returns full recommendation.
    1. Technical analysis
    2. Fundamental analysis
    3. Sentiment analysis
    4. Gemini recommendation (fed all three datasets)

    Scoring weights:
        Technical   — 40%  (normalized –1 to +1)
        Fundamental — 40%  (normalized –1 to +1)
        Sentiment   — 20%  (normalized –1 to +1)
    """

    # Step 1 — resolve company name
    if not company_name:
        info = fetch_stock_info(ticker)
        company_name = info.get("name", ticker.replace(".NS", "").replace(".BO", ""))

    # Step 2 — technical analysis
    print(f"[1/3] Running technical analysis for {ticker}...")
    technical = generate_signals(ticker)
    if "error" in technical:
        return {"error": f"Technical analysis failed: {technical['error']}"}

    # Step 3 — fundamental analysis
    print(f"[2/3] Running fundamental analysis for {ticker}...")
    fundamental = get_fundamental_score(ticker)

    # Step 4 — sentiment analysis
    print(f"[3/3] Running sentiment analysis for {company_name}...")
    sentiment = analyze_sentiment(company_name, ticker)

    # -----------------------------------------------------------------------
    # Step 5 — Combined score
    # technical_score   is already –1 to +1
    # fundamental_score is 0–10, use fundamental_score_normalized (–1 to +1)
    # sentiment_score   is already –1 to +1
    # -----------------------------------------------------------------------
    tech_score  = technical.get("technical_score", 0)       # –1 to +1
    fund_score  = fundamental.get("fundamental_score_normalized", 0)  # –1 to +1
    sent_score  = sentiment.get("sentiment_score", 0)        # –1 to +1

    combined = round(
        (tech_score  * 0.40) +
        (fund_score  * 0.40) +
        (sent_score  * 0.20),
        4
    )

    # -----------------------------------------------------------------------
    # Step 6 — Overall score on 0–10 scale for display
    # Convert combined (–1 to +1) → (0 to 10)
    # -----------------------------------------------------------------------
    overall_score = round((combined + 1) * 5, 2)

    # Component scores on 0–10 scale for display
    tech_score_10  = round((tech_score  + 1) * 5, 2)
    fund_score_10  = fundamental.get("fundamental_score", 5.0)
    sent_score_10  = round((sent_score  + 1) * 5, 2)

    # -----------------------------------------------------------------------
    # Step 7 — Final recommendation label from combined score
    # -----------------------------------------------------------------------
    recommendation_label = _score_to_label(combined)

    # -----------------------------------------------------------------------
    # Step 8 — Gemini (fed all three engines)
    # -----------------------------------------------------------------------
    print(f"Generating Gemini recommendation...")
    gemini_output = get_recommendation(
        ticker=ticker,
        company=company_name,
        technical_data=technical,
        sentiment_data=sentiment,
        fundamental_data=fundamental,   # NEW — pass fundamentals to Gemini
    )

    # -----------------------------------------------------------------------
    # Step 9 — Entry zone, targets, stop-loss, risk/reward
    # Pull from technical engine where available, else from Gemini output.
    # -----------------------------------------------------------------------
    entry_suggestion = technical.get("entry_suggestion")
    stop_loss_atr    = technical.get("stop_loss_atr")
    support_levels   = technical.get("support_resistance", {}).get("support", [])
    resistance_levels= technical.get("support_resistance", {}).get("resistance", [])

    # Entry zone: entry_suggestion ± small buffer (0.5%)
    entry_zone = None
    if entry_suggestion:
        entry_zone = {
            "low":  round(entry_suggestion * 0.995, 2),
            "high": round(entry_suggestion * 1.005, 2),
        }

    # Targets from resistance levels (nearest two above entry)
    target_1 = None
    target_2 = None
    if resistance_levels and entry_suggestion:
        above = sorted([r for r in resistance_levels if r > entry_suggestion])
        if len(above) >= 1:
            target_1 = above[0]
        if len(above) >= 2:
            target_2 = above[1]

    # Risk/reward ratio
    risk_reward = None
    if entry_suggestion and stop_loss_atr and target_1:
        risk   = entry_suggestion - stop_loss_atr
        reward = target_1 - entry_suggestion
        if risk > 0:
            risk_reward = round(reward / risk, 2)

    # Hold period estimate based on bias
    hold_period = _estimate_hold_period(technical.get("bias", "NEUTRAL"), combined)

    # -----------------------------------------------------------------------
    # Final output
    # -----------------------------------------------------------------------
    return {
        "ticker": ticker,
        "company": company_name,

        # Recommendation
        "recommendation": recommendation_label,
        "confidence": _combined_to_confidence(combined),

        # Trade levels
        "entry_zone": entry_zone,
        "target_1": target_1,
        "target_2": target_2,
        "stop_loss": stop_loss_atr,
        "hold_period": hold_period,
        "risk_reward": risk_reward,

        # Scores
        "overall_score": overall_score,
        "technical_score": tech_score_10,
        "fundamental_score": fund_score_10,
        "sentiment_score": sent_score_10,
        "combined_score_raw": combined,     # –1 to +1, useful for Phase 4 Gemini prompt

        # Labels/context
        "technical_bias": technical.get("bias"),
        "fundamental_label": fundamental.get("fundamental_label"),
        "sentiment_label": sentiment.get("label"),

        # Candlestick & divergence context
        "rsi_divergence": technical.get("rsi_divergence"),
        "candlestick_patterns": technical.get("candlestick_patterns", []),
        "weekly_trend": technical.get("weekly_context", {}).get("weekly_trend"),

        # Gemini output (full object — contains engine, reasoning, etc.)
        "gemini": gemini_output,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_to_label(combined: float) -> str:
    """Map –1 to +1 combined score to recommendation label."""
    if combined >= 0.6:
        return "STRONG BUY"
    elif combined >= 0.3:
        return "BUY"
    elif combined >= -0.2:
        return "HOLD"
    elif combined >= -0.5:
        return "SELL"
    else:
        return "STRONG SELL"


def _combined_to_confidence(combined: float) -> int:
    """
    Convert combined score (–1 to +1) to a confidence percentage (0–100).
    Neutral (0.0) = 50%, extremes push toward 95% max.
    """
    raw = int((abs(combined) * 45) + 50)
    return min(raw, 95)


def _estimate_hold_period(bias: str, combined: float) -> str:
    """Rough hold period estimate for delivery trading based on signal strength."""
    if combined >= 0.6:
        return "4–8 weeks"
    elif combined >= 0.3:
        return "2–5 weeks"
    elif combined >= 0.0:
        return "1–3 weeks"
    elif combined >= -0.2:
        return "Avoid / Wait for better entry"
    else:
        return "Do not enter"