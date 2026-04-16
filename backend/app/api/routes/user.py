from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_
from jose import jwt, JWTError

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.db.session import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/profile")
    
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        or_(User.email == user.email, User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code = 401, detail = "User already exists") #400 bad request, server  cannot process.

    new_user = User(
        first_name      = user.first_name,
        last_name       = user.last_name,
        username        = user.username,
        email           = user.email,
        hashed_password = hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return email

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

 
@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):

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

    token = create_access_token({"sub": existing_user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/profile")
def get_user_profile(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    user_details = db.query(User).filter(User.email == current_user).first()
    return user_details