import asyncio
import json
from aiokafka import AIOKafkaConsumer
from collections import defaultdict


# -------------------------------ingestion
# Utility Functions
# -------------------------------

def build_keyword_query(payload):
    """
    Build query from user keywords
    """
    keywords_list = payload.get('keywords', [])

    if not keywords_list:
        return None  # enforce validation

    return f"Topics of interest: {', '.join(keywords_list)}"


def embedd_keyword_query(open_api_client, keyword_query: str):
    """
    Blocking call → will run in thread
    """
    response = open_api_client.embeddings.create(
        input=keyword_query,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


def vector_search(qdrant, query_vector, user_category):
    """
    Perform vector similarity search
    """
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

    # normalize results
    normalized = []
    for r in response.points:
        score = r.score if hasattr(r, "score") else r[1]
        point = r if hasattr(r, "payload") else r[0]
        normalized.append((point, score))

    return normalized


def extract_article_ids(results):
    """
    Aggregate and rank results
    """
    scores = defaultdict(float)

    for point, score in results:
        aid = point.payload.get("article_id")
        if aid:
            scores[aid] += score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [aid for aid, _ in ranked]


async def store_article_id_with_user_id(db, article_ids, user_id):
    """
    Example async DB write (adjust to your ORM)
    """
    if not article_ids:
        return

    # Example pseudo (adapt to your DB)
    await db.execute(
        "INSERT INTO user_recommendations (user_id, article_id) VALUES ($1, $2)",
        [(user_id, aid) for aid in article_ids]
    )


# -------------------------------
# Consumer Service
# -------------------------------

async def consume_and_process(open_api_client, qdrant, db):
    consumer = AIOKafkaConsumer(
        'user_signup_events',
        bootstrap_servers='localhost:9092',
        group_id="rec-service-group",
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    await consumer.start()

    try:
        print("🚀 Listening for signup events...")

        async for msg in consumer:
            try:
                data = msg.value

                payload = {
                    "user_id": data.get('user_id'),
                    "categories": data.get('categories', []),
                    "keywords": data.get('keywords', [])
                }

                # -------------------------
                # Step 0: Validation
                # -------------------------
                if not payload["user_id"]:
                    print("❌ Missing user_id, skipping...")
                    continue

                keyword_query = build_keyword_query(payload)

                if not keyword_query:
                    print(f"⚠️ User {payload['user_id']} has no keywords, skipping...")
                    continue

                # -------------------------
                # Step 1: Embedding (non-blocking)
                # -------------------------
                query_vector = await asyncio.to_thread(
                    embedd_keyword_query,
                    open_api_client,
                    keyword_query
                )

                # -------------------------
                # Step 2: Vector Search
                # -------------------------
                results = vector_search(
                    qdrant,
                    query_vector,
                    payload["categories"]
                )

                # -------------------------
                # Step 3: Ranking
                # -------------------------
                article_ids = extract_article_ids(results)

                # -------------------------
                # Step 4: Store
                # -------------------------
                await store_article_id_with_user_id(
                    db,
                    article_ids,
                    payload["user_id"]
                )

                print(f"✅ Processed user {payload['user_id']}")

            except Exception as e:
                # 🔥 Important: don't crash consumer
                print(f"❌ Error processing message: {e}")

    finally:
        await consumer.stop()