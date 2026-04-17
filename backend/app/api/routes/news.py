from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.news_service import fetch_news_details, store_article, classify_news
from app.models.news import NewsArticle, ArticleCategory

router = APIRouter(prefix = "/news", tags = ['News'])

@router.post("/fetch")
def fetch_news(db: Session = Depends(get_db)):
    articles = fetch_news_details()
    store_article(db, articles)
    
    return {"message": f"store {len(articles)} articles"} 

@router.post("/categotize")
def categorize_news(db: Session = Depends(get_db)):
    news_summary_with_id = db.query(NewsArticle.id, NewsArticle.summary).all() # This give list of tuples.
    
    for news_id, summary in news_summary_with_id:
        
        if not summary:
            continue
        
        exists = db.query(ArticleCategory).filter(
            ArticleCategory.news_id == news_id
        ).first()
        
        if exists:
            continue
        
        label = classify_news(summary)
        article_category = ArticleCategory(
            news_id = news_id,
            category_name = label
        )
        db.add(article_category)
    
    db.commit()