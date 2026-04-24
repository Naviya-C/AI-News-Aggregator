from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

client = QdrantClient(url = "http://localhost:6333")

if not client.collection_exists("news_embedding"):
    client.create_collection(
        collection_name = "news_embedding",
        vectors_config = VectorParams(
            size = 1536,
            distance = Distance.COSINE
            
        )
    )