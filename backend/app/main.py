from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine

import app.models
from app.api.routes import user

app = FastAPI()

# TEMP (replace with Alembic in Day 2)
Base.metadata.create_all(bind=engine)

app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "AI News Aggregator API Running Securely"}