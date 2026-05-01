from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from aiokafka import AIOKafkaProducer
import json

from app.db.session import get_db
from app.models.user import User
from app.core.security import hash_password

router = APIRouter(prefix = "auth", tags = ['auth'])

async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='kafka:9092')
    await producer.start()
    return producer

@router.post("/signup")
async def signup(user_data: dict, db: Session = Depends(get_db)):
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
            
        return {"satatus":"Even Success", "user_id": user.id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code = 400, detail = "str(e)")
        
    