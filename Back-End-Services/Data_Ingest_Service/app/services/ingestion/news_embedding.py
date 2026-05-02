from openai import OpenAI

from app.db.vecotr_db import client
from app.data_processors.chunker import smart_chunk
from app.core.config import OPEN_AI_KEY

class Embedding:
    def embedding_news(self, content, id, cat_name):
        """
        In here this is using for embeddings,
            - content, what embedding
            - id, content belongs id
            - cat_name, which category content belongs
        """
        
        client_openai = OpenAI(api_key = OPEN_AI_KEY)

        list_chunk = smart_chunk(content)
        
        response = client_openai.embeddings.create(
            input = list_chunk,
            model = "text-embedding-3-small"
        )

        vectors = [item.embedding for item in response.data]
        points = []

        for i, vector in enumerate(vectors):
            id_num = id * 1000 + i # In Qdrant id should be either integer or uuid
            points.append({
                "id": id_num,
                "vector": vector,
                "payload": {
                    "article_id": id,
                    "chunk_index": i,
                    "category": cat_name
                }
            })
            
        client.upsert(
            collection_name = "news_embedding",
            points = points
        )