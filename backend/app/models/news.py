from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
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
    embeddings   = relationship("ArticleEmbedding", back_populates="article", cascade="all, delete-orphan")
    interactions = relationship("UserInteraction", back_populates="article")

class ArticleCategory(Base):
    __tablename__ = "article_categories"

    news_id       = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), primary_key=True)
    category_name = Column(String(100), primary_key=True)

    article = relationship("NewsArticle", back_populates="categories")
    
    
class ArticleEmbedding(Base):
    """
    This class for embedd the article and then semantic search and get the user recommendations.
    In here,
        Used: text-embedding-3-large(OpenAI api)
        1$ -> 7.692 million tokens embedding
        Contex_window: 8192 tokens
        Output_vector: dim(3072)
    """
    
    __tablename__ = "article_embeddings"

    news_id     = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), primary_key=True)
    chunk_index = Column(Integer, primary_key=True)
    chunk       = Column(Text, nullable=False)
    embedding   = Column(Vector(3072), nullable=False) # Using ' of OpenAI api' 
    created_at  = Column(DateTime, server_default=func.now())

    article = relationship("NewsArticle", back_populates="embeddings")