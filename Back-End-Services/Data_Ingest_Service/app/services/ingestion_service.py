from app.scraper.api_connector import APIConnector
from app.services.new_categorize import Classifier
from app.models.news import NewsArticle, ArticleCategory

from fastapi import HTTPException
from sqlalchemy import select

CLASSESS = ["business", "entertainment", "general", "health", "science", "sports", "technology"]

class IngestionService:
    """
    API-only ingestion pipeline:
    API → dedup → normalize → return
    """

    def __init__(self, api_key, api_url, db):
        self.api = APIConnector(api_key, api_url)
        self.db = db

    def run_ingestion(self, max_pages = 10, page_size = 20):
        count = 0
        for i in range(1, max_pages + 1):
            results = self.api.fetch(page = i, page_size = page_size)
            if not results:
                continue
            
            results_urls = [result['url'] for result in results]
            existing_usrl_tup = self.db.query(NewsArticle.url).filter(NewsArticle.url.in_(results_urls)).all()
            existing_usrl_list = [ur[0] for ur in existing_usrl_tup]
            new_urls = list(set(results_urls) - set(existing_usrl_list)) # once you convert to the set it order is lost but in here order is not matters.
            
            if not new_urls:
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
                
            count += len(news_art)
            
            if not news_art:
                continue
            
            try:
                self.db.add_all(news_art)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise HTTPException(status_code=500, detail = "Database error") 
            

    def categorize_news(self):
        with self.db.begin():
            final_cat = select(ArticleCategory.news_id).order_by(ArticleCategory.news_id.desc()).limit(1)
            final_cat_news_id = self.db.scalars(final_cat).scalar_one_or_none() # If data table is no any entry it will returns 'None'. Not Zero
            
            news_last = select(NewsArticle.id).order_by(NewsArticle.id.desc()).limit(1)
            news_last_id = self.db.scalar(news_last).scalar_one_or_none()
            
        if final_cat_news_id == news_last_id:
            return "All are updated."
            
        if final_cat_news_id is None:
            final_cat_news_id = 0
        
        classifier = Classifier(CLASSESS)
        
        catg = []
        
        for id in range(final_cat_news_id+1, news_last_id+1):
            stmt = select(NewsArticle.id, NewsArticle.summary.where(NewsArticle.id  == id))
            newId = stmt[0][0]
            label = classifier.classify_news(stmt[0][1])
            
            article_cat = ArticleCategory(
                news_id = newId,
                category_name = label
            )
            
            catg.append(article_cat)
            
        try:
            self.db.add_all(catg)
            self.db.commit()
        except Exception:
            raise HTTPException(status_code = 500, detail = "Database Error")
            
            