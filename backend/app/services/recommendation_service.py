from app.models.user import UserPreferredKeyword, UserPreferredCategory
from app.models.news import NewsArticle

from collections import defaultdict

def build_keyword_query(db, user_id):
    """
    In here, User must need to add atleast one keyword otherwise they can't process next step.
    Assume above, this function built.
    """
    
    rows = db.query(UserPreferredKeyword.keyword_name).filter(UserPreferredKeyword.user_id == user_id).all()
    
    keywords_list = [r[0] for r in rows]
    
    keywords_query = f"Topics of interest: {', '.join(keywords_list)}"
    
    return keywords_query

def embedd_keyword_query(open_api_client, keyword_query:str):
    response = open_api_client.embeddings.create(
        input = keyword_query,
        model = "text-embedding-3-small"
    )
    
    return response.data[0].embedding

def get_user_category(db, user_id):
    row = db.query(UserPreferredCategory.category_name).filter(UserPreferredCategory.user_id == user_id).all()
    category = [cat[0] for cat in row]
    
    return category

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


def fetch_articles_ordered(db, news_ids):
    if not news_ids:
        return []

    rows = db.query(NewsArticle).filter(NewsArticle.id.in_(news_ids)).all()

    row_map = {row.id: row for row in rows}

    ordered = [row_map[nid] for nid in news_ids if nid in row_map]

    # sort by published date (fallback to created_at)
    ordered.sort(
        key = lambda x: x.published_at or x.created_at,
        reverse=True
    )

    return ordered