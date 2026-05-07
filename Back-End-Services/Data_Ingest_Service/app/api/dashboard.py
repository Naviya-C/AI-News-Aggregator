from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.security.validation import validation
from app.db.session import get_db
from app.models.news import NewsArticle, Recommendation

router = APIRouter(prefix = "user")

security = HTTPBearer()

def get_user_id(credentials:str = Depends(security)):
    token = credentials.credentials
    payload = validation(token)
    user_id:str = payload.get("sub")
    
    return int(user_id)
        
@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user_id:int = Depends(get_user_id)):
    results = (
        db.query(NewsArticle).join(Recommendation, NewsArticle.id == Recommendation.news_id)
        .filter(Recommendation.user_id == user_id).all()
    )
    
    return results
    
    