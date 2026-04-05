# services/sentiment.py
from services.news_fetcher import fetch_all_news
from services.finbert import score_text


# CEO/key person statements get boosted weight
CEO_WEIGHT    = 2.0
NORMAL_WEIGHT = 1.0


def analyze_sentiment(company_name: str, ticker: str) -> dict:
    """
    Full sentiment pipeline:
    1. Fetch news
    2. Score each article with FinBERT
    3. Apply CEO weighting
    4. Return aggregated sentiment score + scored articles
    """
    articles = fetch_all_news(company_name, ticker)

    if not articles:
        return {
            "company": company_name,
            "ticker": ticker,
            "sentiment_score": 0.0,
            "label": "neutral",
            "article_count": 0,
            "articles": [],
            "error": "No news articles found"
        }

    scored_articles = []
    total_score     = 0.0
    total_weight    = 0.0

    for article in articles:
        sentiment = score_text(article["text"])
        weight    = CEO_WEIGHT if article["is_ceo_statement"] else NORMAL_WEIGHT

        # Convert to numeric: positive=+1, negative=-1, neutral=0
        numeric = (
            sentiment["positive"] * 1.0 +
            sentiment["negative"] * -1.0 +
            sentiment["neutral"]  * 0.0
        )

        total_score  += numeric * weight
        total_weight += weight

        scored_articles.append({
            "title":          article["title"],
            "source":         article["source"],
            "url":            article["url"],
            "published_at":   article["published_at"],
            "is_ceo_statement": article["is_ceo_statement"],
            "sentiment":      sentiment["label"],
            "confidence":     sentiment["confidence"],
            "positive":       sentiment["positive"],
            "negative":       sentiment["negative"],
            "neutral":        sentiment["neutral"],
            "weight":         weight,
        })

    # Final aggregated score: -1.0 (very negative) to +1.0 (very positive)
    final_score = round(total_score / total_weight, 4) if total_weight > 0 else 0.0
    final_score = max(-1.0, min(1.0, final_score))

    # Label
    if final_score >= 0.15:
        label = "positive"
    elif final_score <= -0.15:
        label = "negative"
    else:
        label = "neutral"

    return {
        "company":         company_name,
        "ticker":          ticker,
        "sentiment_score": final_score,
        "label":           label,
        "article_count":   len(scored_articles),
        "articles":        scored_articles,
    }