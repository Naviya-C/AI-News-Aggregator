from fastapi import FastAPI
from app.db.base import Base # Need to load Base in main cause connect two models(user + news), don't remove. If remove it give table relationship error.
from app.api.routes import user, news

app = FastAPI()

app.include_router(user.router)
app.include_router(news.router)

@app.get("/")
def root():
    return {"message": "AI News Aggregator API Running Securely"}