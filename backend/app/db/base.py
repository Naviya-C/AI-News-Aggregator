from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

from app.models.user import User
from app.models.news import NewsArticle