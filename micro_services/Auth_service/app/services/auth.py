from app.schemas.user_schema import UserCreate, UserLogin
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException


def create_user(user: UserCreate, db: Session):

    existing_user = db.query(User).filter(
        or_(User.email == user.email, User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code = 400, detail = "User already exists") #400 bad request, server  cannot process.

    new_user = User(
        first_name      = user.first_name,
        last_name       = user.last_name,
        username        = user.username,
        email           = user.email,
        hashed_password = hash_password(user.password)
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    return new_user


def login_user(user: UserLogin, db: Session):

    existing_user = db.query(User).filter(
        or_(
            User.email == user.identifier,
            User.username == user.identifier
        )
    ).first()

    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(existing_user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }