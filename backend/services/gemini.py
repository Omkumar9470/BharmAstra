# services/gemini.py
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL  = "gemini-2.0-flash"


def get_recommendation(
    ticker: str,
    company: str,
    technical_data: dict,
    sentiment_data: dict,
    fundamental_data: dict = None,   # Phase 4 — now used
) -> dict:

    # --- Technical ---
    tech_score    = technical_data.get("technical_score", 0)
    tech_bias     = technical_data.get("bias", "NEUTRAL")
    signals       = technical_data.get("signals", [])
    close_price   = technical_data.get("close", "N/A")
    indicators    = technical_data.get("latest_indicators", {})
    entry_suggest = technical_data.get("entry_suggestion", "N/A")
    stop_atr      = technical_data.get("stop_loss_atr", "N/A")
    support       = technical_data.get("support_resistance", {}).get("support", [])
    resistance    = technical_data.get("support_resistance", {}).get("resistance", [])
    rsi_div       = technical_data.get("rsi_divergence", "none")
    patterns      = technical_data.get("candlestick_patterns", [])
    weekly_trend  = technical_data.get("weekly_context", {}).get("weekly_trend", "N/A")
    weekly_rsi    = technical_data.get("weekly_context", {}).get("weekly_rsi", "N/A")

    # --- Sentiment ---
    sent_score    = sentiment_data.get("sentiment_score", 0)
    sent_label    = sentiment_data.get("label", "neutral")
    article_count = sentiment_data.get("article_count", 0)
    top_articles  = sentiment_data.get("articles", [])[:3]

    # --- Fundamental ---
    fund_score    = None
    fund_label    = None
    fund_insights = []
    fund_raw      = {}
    if fundamental_data:
        fund_score    = fundamental_data.get("fundamental_score", "N/A")
        fund_label    = fundamental_data.get("fundamental_label", "N/A")
        fund_insights = fundamental_data.get("insights", [])[:5]
        fund_raw      = fundamental_data.get("raw", {})

    # --- Format helpers ---
    signal_text = "\n".join([
        f"- {s['indicator']}: {s['signal']} — {s['reason']}"
        for s in signals
    ]) or "No signals."

    news_text = "\n".join([
        f"- [{a['sentiment'].upper()}] {a['title']} (Source: {a['source']})"
        for a in top_articles
    ]) or "No recent news found."

    patterns_text = ", ".join([
    p if isinstance(p, str) else p.get("pattern", str(p))
    for p in patterns
]) if patterns else "None detected"

    fund_text = ""
    if fundamental_data:
        fund_text = f"""
=== FUNDAMENTAL ANALYSIS ===
Fundamental Score: {fund_score}/10 ({fund_label})
PE Ratio: {fund_raw.get('pe', 'N/A')}
Revenue Growth YoY: {_fmt_pct(fund_raw.get('revenue_growth_pct'))}
Profit Growth YoY: {_fmt_pct(fund_raw.get('profit_growth_pct'))}
Debt-to-Equity: {_fmt_float(fund_raw.get('debt_to_equity'))}
ROE: {_fmt_pct(fund_raw.get('roe_pct'))}
ROCE: {_fmt_pct(fund_raw.get('roce_pct'))}
Current Ratio: {_fmt_float(fund_raw.get('current_ratio'))}
Promoter Holding: {_fmt_pct(fund_raw.get('promoter_holding_pct'))}
Key Insights:
""" + "\n".join(f"- {i}" for i in fund_insights)

    prompt = f"""
You are an expert Indian stock market analyst specialising in delivery and positional trading (holding for days to weeks, NOT intraday).

Analyze the following complete data for {company} ({ticker}) and give a precise, actionable investment recommendation.

=== TECHNICAL ANALYSIS ===
Current Price: ₹{close_price}
Technical Score: {tech_score} (–1.0 = strongly bearish, +1.0 = strongly bullish)
Overall Bias: {tech_bias}
Weekly Trend: {weekly_trend} | Weekly RSI: {weekly_rsi}
RSI Divergence: {rsi_div}
Candlestick Patterns: {patterns_text}

Indicator Readings:
- RSI: {indicators.get('rsi', 'N/A')}
- MACD Histogram: {indicators.get('macd_diff', 'N/A')}
- Bollinger Band %: {indicators.get('bb_pct', 'N/A')}
- EMA 20: {indicators.get('ema_20', 'N/A')}
- EMA 50: {indicators.get('ema_50', 'N/A')}
- EMA 200: {indicators.get('ema_200', 'N/A')}
- ADX: {indicators.get('adx', 'N/A')}
- ATR: {indicators.get('atr', 'N/A')}

Support Levels: {support}
Resistance Levels: {resistance}
Suggested Entry: ₹{entry_suggest}
ATR-based Stop Loss: ₹{stop_atr}

Signals:
{signal_text}
{fund_text}
=== SENTIMENT ANALYSIS ===
Sentiment Score: {sent_score} (–1.0 = very negative, +1.0 = very positive)
Overall Sentiment: {sent_label.upper()}
Articles Analyzed: {article_count}

Top News Headlines:
{news_text}

=== YOUR TASK ===
This is for DELIVERY/POSITIONAL trading. Consider all three dimensions — technical momentum, business fundamentals, and market sentiment.

Respond in EXACTLY this format — no extra text, no markdown, no explanation outside the fields:

RECOMMENDATION: [STRONG BUY or BUY or HOLD or SELL or STRONG SELL]
CONFIDENCE: [percentage from 0 to 100, e.g. 72]
ENTRY_ZONE_LOW: [price in INR, no ₹ symbol]
ENTRY_ZONE_HIGH: [price in INR, no ₹ symbol]
TARGET_1: [first target price in INR, no ₹ symbol]
TARGET_2: [second, more ambitious target price in INR, no ₹ symbol]
STOP_LOSS: [stop loss price in INR, no ₹ symbol]
HOLD_PERIOD: [e.g. 3–6 weeks]
RISK_REWARD: [ratio, e.g. 2.4]
SUMMARY: [2–3 sentences explaining the recommendation for a delivery trader]
RISKS: [2 key risks, comma separated]
DISCLAIMER: This is for educational purposes only and not financial advice.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        raw_text = response.text.strip()
        result = parse_gemini_response(raw_text, ticker, company)
        result["engine"] = "gemini"
        return result
    except Exception as e:
        print(f"Gemini failed ({str(e)[:80]}), using rule-based fallback.")
        return get_recommendation_local(ticker, company, technical_data, sentiment_data, fundamental_data)


def get_recommendation_local(
    ticker: str,
    company: str,
    technical_data: dict,
    sentiment_data: dict,
    fundamental_data: dict = None,
) -> dict:
    """
    Rule-based fallback — no API needed.
    Activates when Gemini returns 429 or any other exception.
    Now incorporates fundamentals in the combined score.
    """
    tech_score  = technical_data.get("technical_score", 0)
    sent_score  = sentiment_data.get("sentiment_score", 0)
    fund_norm   = fundamental_data.get("fundamental_score_normalized", 0) if fundamental_data else 0

    combined = round(
        (tech_score * 0.40) +
        (fund_norm  * 0.40) +
        (sent_score * 0.20),
        4
    )

    close      = technical_data.get("close", 0) or 0
    signals    = technical_data.get("signals", [])
    indicators = technical_data.get("latest_indicators", {})
    rsi        = indicators.get("rsi") or 50
    tech_bias  = technical_data.get("bias", "NEUTRAL")
    sent_label = sentiment_data.get("label", "neutral")
    fund_label = fundamental_data.get("fundamental_label", "N/A") if fundamental_data else "N/A"

    # Recommendation label
    if combined >= 0.6:
        recommendation = "STRONG BUY"
    elif combined >= 0.3:
        recommendation = "BUY"
    elif combined >= -0.2:
        recommendation = "HOLD"
    elif combined >= -0.5:
        recommendation = "SELL"
    else:
        recommendation = "STRONG SELL"

    confidence = min(int((abs(combined) * 45) + 50), 95)

    # Trade levels
    entry_zone_low = entry_zone_high = target_1 = target_2 = stop_loss = None
    risk_reward = None

    # Prefer ATR-based stop from technical engine
    stop_atr = technical_data.get("stop_loss_atr")
    entry    = technical_data.get("entry_suggestion") or close

    resistance = technical_data.get("support_resistance", {}).get("resistance", [])
    above_entry = sorted([r for r in resistance if r and r > entry]) if resistance else []

    if entry and entry > 0:
        entry_zone_low  = round(entry * 0.995, 2)
        entry_zone_high = round(entry * 1.005, 2)
        stop_loss       = stop_atr if stop_atr else round(entry * 0.95, 2)

        if len(above_entry) >= 1:
            target_1 = above_entry[0]
        else:
            target_1 = round(entry * 1.07, 2)

        if len(above_entry) >= 2:
            target_2 = above_entry[1]
        else:
            target_2 = round(entry * 1.13, 2)

        risk = entry - stop_loss
        if risk > 0:
            risk_reward = round((target_1 - entry) / risk, 2)

    hold_period = _hold_period(combined)

    signal_count = len([s for s in signals if recommendation.endswith(s.get("signal", ""))])
    summary = (
        f"{company} shows a {tech_bias.lower()} technical bias, "
        f"{fund_label.lower()} fundamentals, and {sent_label} sentiment. "
        f"Combined score of {round(combined, 2)} suggests a {recommendation} stance for delivery trading."
    )

    risks = []
    if rsi > 65:
        risks.append("RSI approaching overbought territory")
    if rsi < 35:
        risks.append("RSI in oversold zone — may consolidate further")
    if sent_score < -0.2:
        risks.append("Negative news sentiment could weigh on price")
    if tech_score < -0.2:
        risks.append("Weak technical momentum")
    if fundamental_data and fundamental_data.get("raw", {}).get("debt_to_equity", 0) > 1.5:
        risks.append("High debt levels — watch for interest rate sensitivity")
    if not risks:
        risks.append("Monitor for sudden news or broad market movements")

    return {
        "ticker":         ticker,
        "company":        company,
        "recommendation": recommendation,
        "confidence":     confidence,
        "entry_zone_low":  entry_zone_low,
        "entry_zone_high": entry_zone_high,
        "target_1":       target_1,
        "target_2":       target_2,
        "stop_loss":      stop_loss,
        "hold_period":    hold_period,
        "risk_reward":    risk_reward,
        "summary":        summary,
        "risks":          ", ".join(risks[:2]),
        "disclaimer":     "This is for educational purposes only and not financial advice.",
        "raw_response":   "Generated by rule-based engine (Gemini fallback)",
        "engine":         "rule-based",
    }


def parse_gemini_response(text: str, ticker: str, company: str) -> dict:
    """Parse the structured Gemini response into a clean dict."""
    lines  = text.strip().split("\n")
    result = {
        "ticker":          ticker,
        "company":         company,
        "recommendation":  "HOLD",
        "confidence":      50,
        "entry_zone_low":  None,
        "entry_zone_high": None,
        "target_1":        None,
        "target_2":        None,
        "stop_loss":       None,
        "hold_period":     None,
        "risk_reward":     None,
        "summary":         "",
        "risks":           "",
        "disclaimer":      "",
        "raw_response":    text,
    }

    for line in lines:
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()

        if key == "RECOMMENDATION" and val in ["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]:
            result["recommendation"] = val
        elif key == "CONFIDENCE":
            try:
                result["confidence"] = int(val.replace("%", "").strip())
            except ValueError:
                pass
        elif key == "ENTRY_ZONE_LOW":
            result["entry_zone_low"] = _parse_price(val)
        elif key == "ENTRY_ZONE_HIGH":
            result["entry_zone_high"] = _parse_price(val)
        elif key == "TARGET_1":
            result["target_1"] = _parse_price(val)
        elif key == "TARGET_2":
            result["target_2"] = _parse_price(val)
        elif key == "STOP_LOSS":
            result["stop_loss"] = _parse_price(val)
        elif key == "HOLD_PERIOD":
            result["hold_period"] = val
        elif key == "RISK_REWARD":
            try:
                result["risk_reward"] = float(val)
            except ValueError:
                pass
        elif key == "SUMMARY":
            result["summary"] = val
        elif key == "RISKS":
            result["risks"] = val
        elif key == "DISCLAIMER":
            result["disclaimer"] = val

    return result


# ---------------------------------------------------------------------------
# Tiny helpers
# ---------------------------------------------------------------------------

def _parse_price(val: str):
    """Convert a price string like '2340.5' or 'N/A' to float or None."""
    if not val or val.upper() == "N/A":
        return None
    try:
        return float(val.replace("₹", "").replace(",", "").strip())
    except ValueError:
        return None


def _fmt_pct(val) -> str:
    if val is None:
        return "N/A"
    return f"{val:.1f}%"


def _fmt_float(val) -> str:
    if val is None:
        return "N/A"
    return f"{val:.2f}"


def _hold_period(combined: float) -> str:
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