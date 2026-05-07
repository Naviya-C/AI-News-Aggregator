from app.schemas.user_schema import UserCreate, UserLogin
from app.models.user import User
from app.db.session import get_db
from app.core.security import hash_password, verify_password, create_access_token

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from aiokafka import AIOKafkaProducer
import json

router = APIRouter(prefix = "auth", tags = ['auth'])

async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='kafka:9092')
    await producer.start()
    return producer

@router.post("/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    In here every sign up should need to create producer therefore it's better to have one producer. It reduce cost for create producer each time.
    Use singleton pattern to create producer in future. Then cost getting low.
    """
    try:
        user = User(
            first_name = user_data['first_name'],
            last_name = user_data['last_name'],
            username = user_data['username'],
            email = user_data['email'],
            hashed_password = hash_password(user_data['password'])
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        producer = await kafka_producer()
        
        try:
            event_payload = {
                "user_id": user.id,
                "categories": user_data.get('categories', []),
                "keywords": user_data.get('keywords', [])
            }
            await producer.send_and_wait("user_signup_events", json.dump(event_payload).encode('utf-8'))
        finally:
            await producer.stop()
            
        return {"satatus":"Event Success", "user_id": user.id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code = 400, detail = "str(e)")
        
    

@router.post("/login")
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

    token = create_access_token(
        {
            "sub": str(existing_user.id),
            }
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }