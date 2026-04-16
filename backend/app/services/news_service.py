import requests
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.news import NewsArticle

from app.core.config import NEWS_API_KEY, NEWS_API_URL


now = datetime.now(timezone.utc)
last_24_hours = (now - timedelta(days=1)).strftime("%Y-%m-%d")

def fetch_news():
    params = {
        "apiKey": NEWS_API_KEY,
        "domains": "techcrunch.com,thenextweb.com",
        "from": last_24_hours,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 20,
        "page": 1
    }
    
    response = requests.get(NEWS_API_URL, params = params)
    
    if response != 200:
        return []
    
    data = response.json()
    
def store_article(db: Session, artcles: list[dict]):
    
    for article in artcles:
        exists = db.query(NewsArticle).filter(
            NewsArticle.url == article['url']
        ).first()
        
        if exists:
            continue
        
        new_article = NewsArticle(
            title = article['title'],
            content = article['content'],
            summary = article['description'],
            url = article['url'],
            source_name = article.source['name'],
            published_at = article['publishedAt']
        )
        
        db.add(new_article)
        
    db.commit()
        