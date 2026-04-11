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
) -> dict:

    tech_score    = technical_data.get("technical_score", 0)
    tech_bias     = technical_data.get("bias", "NEUTRAL")
    signals       = technical_data.get("signals", [])
    close_price   = technical_data.get("close", "N/A")
    indicators    = technical_data.get("latest_indicators", {})

    sent_score    = sentiment_data.get("sentiment_score", 0)
    sent_label    = sentiment_data.get("label", "neutral")
    article_count = sentiment_data.get("article_count", 0)
    top_articles  = sentiment_data.get("articles", [])[:3]

    signal_text = "\n".join([
        f"- {s['indicator']}: {s['signal']} — {s['reason']}"
        for s in signals
    ])

    news_text = "\n".join([
        f"- [{a['sentiment'].upper()}] {a['title']} (Source: {a['source']})"
        for a in top_articles
    ]) or "No recent news found."

    prompt = f"""
You are an expert Indian stock market analyst. Analyze the following data for {company} ({ticker}) and give a clear investment recommendation.

=== TECHNICAL ANALYSIS ===
Current Price: ₹{close_price}
Technical Score: {tech_score} (scale: -1.0 bearish to +1.0 bullish)
Overall Bias: {tech_bias}

Indicator Readings:
- RSI: {indicators.get('rsi', 'N/A')}
- MACD Histogram: {indicators.get('macd_diff', 'N/A')}
- Bollinger Band %: {indicators.get('bb_pct', 'N/A')}
- EMA 20: {indicators.get('ema_20', 'N/A')}
- EMA 50: {indicators.get('ema_50', 'N/A')}
- SMA 200: {indicators.get('sma_200', 'N/A')}

Signals:
{signal_text}

=== SENTIMENT ANALYSIS ===
Sentiment Score: {sent_score} (scale: -1.0 very negative to +1.0 very positive)
Overall Sentiment: {sent_label.upper()}
Articles Analyzed: {article_count}

Top News Headlines:
{news_text}

=== YOUR TASK ===
Based on the above data, provide your recommendation in EXACTLY this format — no extra text:

RECOMMENDATION: [BUY or HOLD or SELL]
CONFIDENCE: [HIGH or MEDIUM or LOW]
TARGET_PRICE: [estimated short-term target price in INR, or N/A]
STOP_LOSS: [suggested stop loss price in INR, or N/A]
SUMMARY: [2-3 sentences explaining the recommendation in simple terms]
RISKS: [1-2 key risks to watch out for]
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
        print(f"Gemini failed ({str(e)[:80]}...), using rule-based fallback.")
        return get_recommendation_local(ticker, company, technical_data, sentiment_data)


def get_recommendation_local(
    ticker: str,
    company: str,
    technical_data: dict,
    sentiment_data: dict,
) -> dict:
    """
    Pure rule-based recommendation — no API needed.
    Used as fallback when Gemini quota is exhausted.
    """
    tech_score  = technical_data.get("technical_score", 0)
    sent_score  = sentiment_data.get("sentiment_score", 0)
    combined    = (tech_score * 0.6) + (sent_score * 0.4)
    close       = technical_data.get("close", 0) or 0
    signals     = technical_data.get("signals", [])
    indicators  = technical_data.get("latest_indicators", {})
    rsi         = indicators.get("rsi") or 50
    tech_bias   = technical_data.get("bias", "NEUTRAL")
    sent_label  = sentiment_data.get("label", "neutral")

    # --- Recommendation ---
    if combined >= 0.3:
        recommendation = "BUY"
        confidence     = "HIGH" if combined >= 0.6 else "MEDIUM"
    elif combined <= -0.3:
        recommendation = "SELL"
        confidence     = "HIGH" if combined <= -0.6 else "MEDIUM"
    else:
        recommendation = "HOLD"
        confidence     = "LOW"

    # --- Target price & stop loss ---
    if close and close > 0:
        if recommendation == "BUY":
            target    = round(close * 1.08, 2)
            stop_loss = round(close * 0.95, 2)
        elif recommendation == "SELL":
            target    = round(close * 0.93, 2)
            stop_loss = round(close * 1.04, 2)
        else:
            target    = round(close * 1.04, 2)
            stop_loss = round(close * 0.97, 2)
    else:
        target = stop_loss = None

    # --- Summary ---
    signal_count = len([s for s in signals if s["signal"] == recommendation])
    summary = (
        f"{company} shows a {tech_bias.lower()} technical bias with "
        f"{sent_label} market sentiment. "
        f"Combined score of {round(combined, 2)} suggests a {recommendation} stance. "
        f"{signal_count} out of {len(signals)} indicators support this view."
    )

    # --- Risks ---
    risks = []
    if rsi > 65:
        risks.append("RSI approaching overbought territory")
    if rsi < 35:
        risks.append("RSI approaching oversold territory")
    if sent_score < -0.2:
        risks.append("Negative news sentiment could weigh on price")
    if tech_score < -0.2:
        risks.append("Weak technical momentum")
    if not risks:
        risks.append("Monitor for sudden news or market-wide movements")

    return {
        "ticker":         ticker,
        "company":        company,
        "recommendation": recommendation,
        "confidence":     confidence,
        "target_price":   f"₹{target}" if target else None,
        "stop_loss":      f"₹{stop_loss}" if stop_loss else None,
        "summary":        summary,
        "risks":          ", ".join(risks),
        "disclaimer":     "This is for educational purposes only and not financial advice.",
        "raw_response":   "Generated by rule-based engine (Gemini fallback)",
        "engine":         "rule-based"
    }


def parse_gemini_response(text: str, ticker: str, company: str) -> dict:
    lines  = text.strip().split("\n")
    result = {
        "ticker": ticker,
        "company": company,
        "recommendation": "HOLD",
        "confidence": "LOW",
        "target_price": None,
        "stop_loss": None,
        "summary": "",
        "risks": "",
        "disclaimer": "",
        "raw_response": text,
    }

    for line in lines:
        line = line.strip()
        if line.startswith("RECOMMENDATION:"):
            val = line.replace("RECOMMENDATION:", "").strip()
            if val in ["BUY", "HOLD", "SELL"]:
                result["recommendation"] = val
        elif line.startswith("CONFIDENCE:"):
            val = line.replace("CONFIDENCE:", "").strip()
            if val in ["HIGH", "MEDIUM", "LOW"]:
                result["confidence"] = val
        elif line.startswith("TARGET_PRICE:"):
            val = line.replace("TARGET_PRICE:", "").strip()
            result["target_price"] = None if val == "N/A" else val
        elif line.startswith("STOP_LOSS:"):
            val = line.replace("STOP_LOSS:", "").strip()
            result["stop_loss"] = None if val == "N/A" else val
        elif line.startswith("SUMMARY:"):
            result["summary"] = line.replace("SUMMARY:", "").strip()
        elif line.startswith("RISKS:"):
            result["risks"] = line.replace("RISKS:", "").strip()
        elif line.startswith("DISCLAIMER:"):
            result["disclaimer"] = line.replace("DISCLAIMER:", "").strip()

    return result