from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.db.base import Base
from sqlalchemy.sql import func

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    first_name      = Column(String(25), nullable=False)
    last_name       = Column(String(25), nullable=False)
    username        = Column(String(15), unique=True, index=True, nullable=False)
    email           = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at      = Column(DateTime, server_default=func.now())

    # relationships
    preferred_categories = relationship("UserPreferredCategory", back_populates="user", cascade="all, delete-orphan")
    preferred_keywords   = relationship("UserPreferredKeyword",  back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    """
    Master list of categories (e.g. 'LLMs', 'Robotics').
    Populated by admin/seed data — NOT per user.
    """
    __tablename__ = "categories"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    followers = relationship("UserPreferredCategory", back_populates="category")


class UserPreferredCategory(Base):
    """
    Junction table — User <-> Category (many-to-many).
    One row = one user follows one category.
    A user can follow many categories, each as a separate row.
    """
    __tablename__ = "user_preferred_categories"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id",      ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at  = Column(DateTime, server_default=func.now())

    # prevents duplicate (user, category) pairs at DB level
    __table_args__ = (UniqueConstraint("user_id", "category_id", name="uq_user_category"),)

    user     = relationship("User",     back_populates="preferred_categories")
    category = relationship("Category", back_populates="followers")


class Tag(Base):
    """
    Normalized keyword/tag pool (e.g. 'GPT-5', 'OpenAI', 'diffusion models').
    Shared across users and articles — not duplicated per user.
    """
    __tablename__ = "tags"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    preferred_by = relationship("UserPreferredKeyword", back_populates="tag")


class UserPreferredKeyword(Base):
    """
    Junction table — User <-> Tag (many-to-many).
    One row = one user is interested in one tag/keyword.
    """
    __tablename__ = "user_preferred_keywords"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tag_id     = Column(Integer, ForeignKey("tags.id",  ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # prevents duplicate (user, tag) pairs at DB level
    __table_args__ = (UniqueConstraint("user_id", "tag_id", name="uq_user_tag"),)

    user = relationship("User", back_populates="preferred_keywords")
    tag  = relationship("Tag",  back_populates="preferred_by")
    
    
    