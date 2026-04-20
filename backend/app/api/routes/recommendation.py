from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.db.session import get_db
from app.core.llm import open_ai_client
from app.db.vecotr_db import client
from app.services.recommendation_service import (
    build_keyword_query,
    embedd_keyword_query,
    get_user_category,
    vector_search,
    extract_article_ids,
    fetch_articles_ordered
    )


router = APIRouter(prefix = "/debug")


@router.get("/recommend/{user_id}")
def debug_recommend(user_id: int, db: Session = Depends(get_db)):
    query = build_keyword_query(db, user_id)
    vector = embedd_keyword_query(open_ai_client, query)
    categories = get_user_category(db, user_id)

    results = vector_search(client, vector, categories)

    # print raw results for inspection
    debug = [
        {
            "score": score,
            "article_id": point.payload.get("article_id"),
            "category": point.payload.get("category")
        }
        for point, score in results
    ]

    news_ids = extract_article_ids(results)
    articles = fetch_articles_ordered(db, news_ids)

    return {
        "query": query,
        "categories": categories,
        "raw_results": debug,
        "final_articles": [
            {"id": a.id, "title": a.title}
            for a in articles
        ]
    }