import requests
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.models.news import NewsArticle
from app.core.config import NEWS_API_KEY, NEWS_API_URL


now = datetime.now(timezone.utc)
last_24_hours = (now - timedelta(days=1)).strftime("%Y-%m-%d")

def fetch_news_details():
    params = {
        "apiKey": NEWS_API_KEY,
        "domains": "techcrunch.com,thenextweb.com",
        "from": last_24_hours,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 100,
        "page": 1
    }
    
    try:
        response = requests.get(NEWS_API_URL, params = params)
        response.raise_for_status()
    except:
        return []
    
    data = response.json()
    return data.get("articles", [])
    
    
def store_article(db: Session, articles: list[dict]):
    
    for article in articles:
        exists = db.query(NewsArticle).filter(
            NewsArticle.url == article.get("url")
        ).first()
        
        if exists:
            continue
        
        new_article = NewsArticle(
            title = article.get("title"),
            content = article.get("content"),
            summary = article.get("description"),
            url = article.get("url"),
            source_name = article.get("source", {}).get("name"),
            published_at = datetime.fromisoformat(
                article["publishedAt"].replace("Z", "+00:00")
            ) if article.get("publishedAt") else None
        )
        
        db.add(new_article)
        
    db.commit()
        