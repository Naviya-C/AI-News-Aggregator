from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance

from app.core.config import QDRANT_URL, QDRANT_API_KEY
 
client = QdrantClient(
    url = QDRANT_URL,
    api_key = QDRANT_API_KEY
    )

if not client.collection_exists("news_embedding"):
    client.create_collection(
        collection_name = "news_embedding",
        vectors_config = VectorParams(
            size = 1536,
            distance = Distance.COSINE
        )
    )
    
client.create_payload_index(
    collection_name = "news_embedding",
    field_name = "article_id",
    field_schema = models.PayloadSchemaType.INTEGER  
)

