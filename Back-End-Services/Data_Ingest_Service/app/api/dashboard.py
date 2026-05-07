from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.security.validation import validation
from app.db.session import get_db
from app.models.news import NewsArticle, Recommendation

router = APIRouter(prefix = "user")


    
    