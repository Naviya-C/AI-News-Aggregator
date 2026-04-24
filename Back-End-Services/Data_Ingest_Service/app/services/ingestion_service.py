from app.scraper.api_connector import APIConnector
from app.models.news import NewsArticle

from fastapi import HTTPException

class IngestionService:
    """
    API-only ingestion pipeline:
    API → dedup → normalize → return
    """

    def __init__(self, api_key, api_url, db):
        self.api = APIConnector(api_key, api_url)
        self.db = db

    def run_ingestion(self, max_pages = 10, page_size = 20):
        for i in range(1, max_pages + 1):
            results = self.api.fetch(page = i, page_size = page_size)
            if results is None:
                continue
            
            results_urls = [result['url'] for result in results]
            existing_usrl_tup = self.db.query(NewsArticle.url).filter(NewsArticle.url.in_(results_urls)).all()
            existing_usrl_list = [ur[0] for ur in existing_usrl_tup]
            new_urls = list(set(results_urls) - set(existing_usrl_list)) # once you convert to the set it order is lost but in here order is not matters.
            
            if len(new_urls) == 0:
                continue
            
            database_includeing_results = [result for result in results if result['url'] in new_urls]
            
            news_art = []
            for res in database_includeing_results:
                news = NewsArticle(
                    title = res['title'],
                    content = res['content'],
                    summary = res['summary'],
                    url = res['url'],
                    source_name = res['source_name'],
                    published_at = res['published_at']
                )
                news_art.append(news)
            
            if news_art is None:
                continue
            
            try:
                self.db.add_all(news_art)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise HTTPException(status_code=500, detail = "Database error") 
            

        
        
        
        
        