from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.news_service import fetch_news, store_article

router = APIRouter(prefix = "/news", tags = ['News'])

@router.post("/fetch")
def fetch_news(db: Session = Depends(get_db)):
    articles = fetch_news()
    store_article(db, articles)
    
    return {"message": f"store {len(articles)} articles"} 