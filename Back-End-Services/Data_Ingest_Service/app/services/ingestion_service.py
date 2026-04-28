from app.scraper.api_connector import APIConnector
from app.services.new_categorize import Classifier
from app.models.news import NewsArticle, ArticleCategory
from app.services.news_embedding import Embedding
from app.db.vecotr_db import client

from fastapi import HTTPException
from sqlalchemy import select
from qdrant_client import models

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
        
        self.db.rollback()
        
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
            
        self.db.rollback() # Should need to close transaction before start 'with.db.begin()'. Start transaction in 'stmt'.
        
        with self.db.begin():
            self.db.add_all(new_categories)
        
        return "Categorization complete"
    
    
    def news_embedding(self):
        result, _ = client.scroll(
            collection_name = "news_embedding",
            limit = 1,
            with_payload = True,
            order_by = models.OrderBy(
                key = "article_id",
                direction = models.Direction.DESC
            )
        )
        
        last_news_id_in_vecDB = result[0].payload['article_id'] if result else 0
            
            
        with self.db.begin():
            stmt = (
                select(NewsArticle.id, NewsArticle.content, ArticleCategory.category_name)
                .join(ArticleCategory, ArticleCategory.news_id == NewsArticle.id)
                .where(NewsArticle.id > last_news_id_in_vecDB)
                .order_by(NewsArticle.id.asc())
                .execution_options(yield_per=100) # Fetches 100 rows at a time
            )
            
            # Iterating directly over the result is memory efficient
            result_stream = self.db.execute(stmt)
            
            embedding = Embedding()
            count = 0
            
            for art_id, content, cat_name in result_stream:
                if content:
                    embedding.embedding_news(id = art_id, content = content, cat_name = cat_name)
                    count += 1
                    
        return f"Successfully embedded {count} articles"
    
    
    def run_full_pipeline(self):
        """Executes the entire ETL flow in order."""
        print("Starting Step 1: Ingestion...")
        self.run_ingestion()
        print("Completed step 1")
        
        print("Starting Step 2: Categorization...")
        cat_status = self.categorize_news()
        print(f"Categorization status: {cat_status}")
        
        print("Starting Step 3: Embedding...")
        embed_status = self.news_embedding()
        print(f"Embedding status: {embed_status}")
        
        return {"status": "Complete", "details": embed_status}

