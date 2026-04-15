from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

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
