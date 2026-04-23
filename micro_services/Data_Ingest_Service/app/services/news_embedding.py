from fastapi import Depends
from openai import OpenAI
from sqlalchemy.orm import Session

from app.models.news import NewsArticle, ArticleCategory
from app.db.vecotr_db import client
from app.data_processors.chunker import smart_chunk
from app.core.config import OPEN_AI_KEY

def embedding_news(db: Session):
    client_openai = OpenAI(api_key = OPEN_AI_KEY)
    
    news_content = db.query(NewsArticle.id, NewsArticle.content).all()
    
    for news_id, content in news_content:
        
        if not content:
            continue
        
        list_chunk = smart_chunk(content)
        
        category = db.query(ArticleCategory).filter(ArticleCategory.news_id == news_id).first() # Fist returns the <ArticleCategory object> OR None
        cat_name = category.category_name if category else None
        
        response = client_openai.embeddings.create(
            input = list_chunk,
            model = "text-embedding-3-small"
        )
    
        vectors = [item.embedding for item in response.data]
        points = []
    
        for i, vector in enumerate(vectors):
            id_num = news_id * 1000 + i # In Qdrant id should be either integer or uuid
            points.append({
                "id": id_num,
                "vector": vector,
                "payload": {
                    "article_id": news_id,
                    "chunk_index": i,
                    "category": cat_name
                }
            })
            
        client.upsert(
            collection_name = "news_embedding",
            points = points
        )