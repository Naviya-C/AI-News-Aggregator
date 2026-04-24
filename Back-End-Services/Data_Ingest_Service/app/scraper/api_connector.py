import requests
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.scraper.base import BaseScraper


class APIConnector(BaseScraper):

    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url

    def fetch(self, page = 1, page_size = 20):
        
        now = datetime.now(timezone.utc)
        last_24_hours = (now - timedelta(days = 1)).strftime("%Y-%m-%d")
        
        params = {
            "apiKey": self.api_key,
            "domains": "techcrunch.com,thenextweb.com",
            "from": last_24_hours,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": page_size,
            "page": page
        }

        try:
            response = requests.get(self.api_url, params = params, timeout = 15)
            response.raise_for_status()
            data = response.json()
            
        except Exception:
            return []

        articles = data.get("articles", [])

        results = []
        for article in articles:
            url = article.get("url")
            
            if not url:
                continue 

            results.append({
                "title": article.get("title"),
                "content": article.get("content"),
                "summary": article.get("description"),
                "url": url,
                "source_name": article.get("source", {}).get("name"),
                "published_at": (
                    datetime.fromisoformat(
                        article["publishedAt"].replace("Z", "+00:00")
                    )
                    if article.get("publishedAt")
                    else None
                )
            })

        return results