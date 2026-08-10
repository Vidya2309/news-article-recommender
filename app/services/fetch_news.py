import requests
from datetime import datetime, timezone
from app.models import db, Article
from config import Config

NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

def fetch_and_store_news(category="general", country="us", page_size=20):
    params = {
        "apiKey": Config.NEWS_API_KEY,
        "category": category,
        "country": country,
        "pageSize": page_size,
    }

    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[fetch_news] Request failed: {e}")
        return 0

    data = response.json()
    articles = data.get("articles", [])

    new_count = 0
    for item in articles:
        url = item.get("url")
        if not url:
            continue

        # Skip if already in DB (dedupe by URL)
        existing = Article.query.filter_by(url=url).first()
        if existing:
            continue

        published_at = None
        if item.get("publishedAt"):
            try:
                published_at = datetime.fromisoformat(
                    item["publishedAt"].replace("Z", "+00:00")
                )
            except ValueError:
                published_at = None

        article = Article(
            headline=item.get("title") or "Untitled",
            description=item.get("description"),
            url=url,
            source=(item.get("source") or {}).get("name"),
            category=category,
            published_at=published_at,
            image_url=item.get("urlToImage"),
        )
        db.session.add(article)
        new_count += 1

    db.session.commit()
    print(f"[fetch_news] Added {new_count} new articles.")
    return new_count
def fetch_tamil_nadu_news(page_size=20):
    """Fetch Tamil Nadu-related news using keyword search (NewsAPI /everything)."""
    params = {
        "apiKey": Config.NEWS_API_KEY,
        "q": "Tamil Nadu",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
    }

    try:
        response = requests.get(
            "https://newsapi.org/v2/everything", params=params, timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[fetch_tamil_nadu_news] Request failed: {e}")
        return 0

    data = response.json()
    articles = data.get("articles", [])

    new_count = 0
    for item in articles:
        url = item.get("url")
        if not url:
            continue

        existing = Article.query.filter_by(url=url).first()
        if existing:
            continue

        published_at = None
        if item.get("publishedAt"):
            try:
                published_at = datetime.fromisoformat(
                    item["publishedAt"].replace("Z", "+00:00")
                )
            except ValueError:
                published_at = None

        article = Article(
    headline=item.get("title") or "Untitled",
    description=item.get("description"),
    url=url,
    source=(item.get("source") or {}).get("name"),
   category="tamil_nadu",          # or "tamil_nadu" in the other function
    published_at=published_at,
    image_url=item.get("urlToImage"),   # NEW
)
        db.session.add(article)
        new_count += 1

    db.session.commit()
    print(f"[fetch_tamil_nadu_news] Added {new_count} new articles.")
    return new_count