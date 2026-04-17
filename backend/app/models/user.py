from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from app.db.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users" 

    id              = Column(Integer, primary_key=True, index=True)
    first_name      = Column(String(25), nullable=False)
    last_name       = Column(String(25), nullable=False)
    username        = Column(String(15), unique=True, index=True, nullable=False)
    email           = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at      = Column(DateTime, server_default=func.now())

    
    preferred_categories = relationship("UserPreferredCategory", back_populates="user", cascade="all, delete-orphan")
    preferred_keywords   = relationship("UserPreferredKeyword",  back_populates="user", cascade="all, delete-orphan")
    interactions         = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
 
class UserPreferredCategory(Base):
    """
    Using user_id and Category name as composite key.
    """
    __tablename__ = "user_preferred_categories"

    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    category_name = Column(String(100), primary_key=True)
    
    created_at    = Column(DateTime, server_default=func.now())
    
    #relationship
    user = relationship("User", back_populates="preferred_categories")

class UserPreferredKeyword(Base):
    """
    Use user_id and keyword_name as composite key.
    """
    __tablename__ = "user_preferred_keywords"

    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    keyword_name  = Column(String(100), primary_key=True)
    created_at    = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="preferred_keywords")
    

class UserInteraction(Base):
    __tablename__ = "user_interactions"

    # composite PK — one row per user per article per interaction type
    id                = Column(Integer, primary_key=True)
    user_id           = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id        = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False)
    interaction_type  = Column(String(50), nullable=False)  # "read", "like", "share", "click", "skip"
    time_spent        = Column(Integer, default=0, nullable=False)
    interaction_score = Column(Float,   default=1.0)
    interact_at       = Column(DateTime, server_default=func.now())

    user     = relationship("User", back_populates="interactions")
    article  = relationship("NewsArticle", back_populates="interactions") 