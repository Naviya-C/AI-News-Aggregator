from app.scraper.api_connector import APIConnector
from app.services.new_categorize import Classifier
from app.models.news import NewsArticle, ArticleCategory
from app.services.news_embedding import embedding_news

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
        classifier = Classifier(CLASSESS)
        
        with self.db.begin():
            # scalar normally return the oject but it depends on what you put inside to the select(), in here I put directly a one column therefore it returns only values rather returning any object.
            last_recorded_news_id_in_ArticleCat = self.db.scalar(select(ArticleCategory.news_id).order_by(ArticleCategory.news_id.desc()).limit(1)) or 0         
            news_last_id_in_NewsArticle = self.db.scalar(select(NewsArticle.id).order_by(NewsArticle.id.desc()).limit(1))
            
        if last_recorded_news_id_in_ArticleCat == news_last_id_in_NewsArticle:
            return "All are updated."
        if last_recorded_news_id_in_ArticleCat > news_last_id_in_NewsArticle:
            return "Tables has conflict"
            
        new_categories = []
        
        for id in range(last_recorded_news_id_in_ArticleCat+1, news_last_id_in_NewsArticle+1):
            stmt = self.db.execute(select(NewsArticle.id, NewsArticle.summary).where(NewsArticle.id  == id)).first()
            if stmt:
                newsId = stmt[0]
                label = classifier.classify_news(stmt[1])
            else:
                continue
            
            article_cat = ArticleCategory(
                news_id = newsId,
                category_name = label
            )
                    
            new_categories.append(article_cat)
            
        with self.db.begin():
            self.db.add_all(new_categories)
        
        return "Categorization complete"
    
    