# services/news_fetcher.py
import os
import requests
import feedparser
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# RSS feeds — completely free, no limits
RSS_FEEDS = {
    "moneycontrol": "https://www.moneycontrol.com/rss/latestnews.xml",
    "economic_times": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "business_standard": "https://www.business-standard.com/rss/markets-106.rss",
}

# Keywords that indicate a CEO/important person statement
CEO_KEYWORDS = [
    "ceo", "chairman", "md", "managing director", "founder",
    "chief executive", "president", "director", "cfo", "coo",
    "said", "stated", "announced", "declared", "expects", "predicts"
]


def fetch_newsapi(query: str, max_articles: int = 10) -> list:
    """Fetch news from NewsAPI for a given stock/company query."""
    if not NEWSAPI_KEY:
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": max_articles,
            "apiKey": NEWSAPI_KEY,
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if data.get("status") != "ok":
            return []

        articles = []
        for a in data.get("articles", []):
            articles.append({
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "source": a.get("source", {}).get("name", ""),
                "url": a.get("url", ""),
                "published_at": a.get("publishedAt", ""),
                "text": f"{a.get('title', '')}. {a.get('description', '')}",
                "is_ceo_statement": _is_ceo_statement(
                    a.get("title", "") + " " + a.get("description", "")
                ),
            })
        return articles
    except Exception as e:
        print(f"NewsAPI error: {e}")
        return []


def fetch_rss(company_name: str, max_articles: int = 10) -> list:
    """Fetch and filter RSS feed articles matching the company name."""
    articles = []
    company_lower = company_name.lower()

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:30]:  # scan top 30, filter by relevance
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                combined = f"{title} {summary}".lower()

                if company_lower in combined:
                    articles.append({
                        "title": title,
                        "description": summary,
                        "source": source_name,
                        "url": entry.get("link", ""),
                        "published_at": entry.get("published", ""),
                        "text": f"{title}. {summary}",
                        "is_ceo_statement": _is_ceo_statement(combined),
                    })

            if len(articles) >= max_articles:
                break
        except Exception as e:
            print(f"RSS error ({source_name}): {e}")

    return articles[:max_articles]


def fetch_all_news(company_name: str, ticker: str) -> list:
    """
    Combine NewsAPI + RSS results.
    Deduplicate by title.
    """
    newsapi_results = fetch_newsapi(company_name, max_articles=8)
    rss_results     = fetch_rss(company_name, max_articles=8)

    all_articles = newsapi_results + rss_results

    # Deduplicate by title
    seen = set()
    unique = []
    for a in all_articles:
        title = a["title"].lower().strip()
        if title and title not in seen:
            seen.add(title)
            unique.append(a)

    return unique


def _is_ceo_statement(text: str) -> bool:
    """Check if article likely contains a CEO/key person statement."""
    text_lower = text.lower()
    matches = sum(1 for kw in CEO_KEYWORDS if kw in text_lower)
    return matches >= 2