import asyncio
import json
from aiokafka import AIOKafkaConsumer
from collections import defaultdict


# --- SERVICE 1: The Consumer ---
async def consume_and_process():
    """
    This is used for signup event. The initial part of the user recommendations
    """
    consumer = AIOKafkaConsumer(
        'user_signup_events',
        bootstrap_servers='localhost:9092', # Localhost for local machine
        group_id="rec-service-group"
    )
    
    await consumer.start()

    try:
        print("Listening for signup events...")
        async for msg in consumer:
            data = json.loads(msg.value.decode('utf-8'))
            payload = {
                "user_id": data['user_id'],
                "categories": data.get('categories', []),
                "keywords": data.get('keywords', [])
            }
                
    finally:
        await consumer.stop()
        
    return payload

asyncio.run(consume_and_process())


def build_keyword_query(payload):
    """
    In here, User must need to add atleast one keyword otherwise they can't process next step.
    Assume above, this function built.
    """
        
    keywords_list = payload['keywords']
    
    keywords_query = f"Topics of interest: {', '.join(keywords_list)}"
    
    return keywords_query

def embedd_keyword_query(open_api_client, keyword_query:str):
    response = open_api_client.embeddings.create(
        input = keyword_query,
        model = "text-embedding-3-small"
    )
    
    return response.data[0].embedding

def vector_search(qdrant, query_vector, user_category):

    query_filter = None 
    
    if user_category:
        query_filter = {
            "must": [
                {
                    "key": "category",
                    "match": {"any": user_category}
                }
            ]
        }
        
    response = qdrant.query_points(
        collection_name="news_embedding",
        query=query_vector,
        limit=5,
        query_filter=query_filter
    )

    # 🔥 normalize results to (point, score)
    normalized = []
    for r in response.points:
        if isinstance(r, tuple):
            normalized.append(r)
        else:
            normalized.append((r, r.score))

    return normalized

def extract_article_ids(results):
    scores = defaultdict(float)

    for r in results:
        # handle tuple format
        if isinstance(r, tuple):
            point, score = r
        else:
            point, score = r, r.score

        aid = point.payload["article_id"]
        scores[aid] += score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [aid for aid, _ in ranked]

def store_article_id_with_user_id(db, article_ids: list, user_id):
    pass