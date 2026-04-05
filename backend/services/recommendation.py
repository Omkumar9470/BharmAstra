# services/recommendation.py
from services.technical import generate_signals
from services.sentiment import analyze_sentiment
from services.gemini import get_recommendation
from services.stock_data import fetch_stock_info


def generate_full_recommendation(ticker: str, company_name: str = None) -> dict:
    """
    Master function — runs all 3 engines and returns full recommendation.
    1. Technical analysis
    2. Sentiment analysis  
    3. Gemini recommendation
    """

    # Step 1 — get company name if not provided
    if not company_name:
        info = fetch_stock_info(ticker)
        company_name = info.get("name", ticker.replace(".NS", "").replace(".BO", ""))

    # Step 2 — run technical analysis
    print(f"Running technical analysis for {ticker}...")
    technical = generate_signals(ticker)
    if "error" in technical:
        return {"error": f"Technical analysis failed: {technical['error']}"}

    # Step 3 — run sentiment analysis
    print(f"Running sentiment analysis for {company_name}...")
    sentiment = analyze_sentiment(company_name, ticker)

    # Step 4 — combined score (60% technical, 40% sentiment)
    tech_score  = technical.get("technical_score", 0)
    sent_score  = sentiment.get("sentiment_score", 0)
    combined    = round((tech_score * 0.6) + (sent_score * 0.4), 4)

    # Step 5 — get Gemini recommendation
    print(f"Generating Gemini recommendation...")
    recommendation = get_recommendation(
        ticker=ticker,
        company=company_name,
        technical_data=technical,
        sentiment_data=sentiment,
    )

    return {
        "ticker": ticker,
        "company": company_name,
        "combined_score": combined,
        "technical_score": tech_score,
        "sentiment_score": sent_score,
        "technical_bias": technical.get("bias"),
        "sentiment_label": sentiment.get("label"),
        "recommendation": recommendation,
    }