from fastapi import FastAPI
from app.services.auth import router

app = FastAPI()

app.include_router(router)