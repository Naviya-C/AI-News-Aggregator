from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
 
 
class NewsArticle(Base):
    __tablename__ = "news_articles"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(500), nullable=False)
    content      = Column(Text)
    summary      = Column(Text)
    url          = Column(String(1000), unique=True, nullable=False)
    source_name  = Column(String(255))
    published_at = Column(DateTime)
    created_at   = Column(DateTime, server_default=func.now())

    categories   = relationship("ArticleCategory", back_populates="article", cascade="all, delete-orphan")


class ArticleCategory(Base):
    __tablename__ = "article_categories"

    news_id       = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), primary_key=True)
    category_name = Column(String(100), primary_key=True)

    article = relationship("NewsArticle", back_populates="categories")
    
class Recommendation(Base):
    __tablename__ = "user_news_recommendations"
    
    user_id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), primary_key=True)
    
    