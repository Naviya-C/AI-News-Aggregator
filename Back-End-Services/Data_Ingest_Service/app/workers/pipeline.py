from app.services.ingestion.ingestion_service import IngestionService
from app.core.config import NEWS_API_URL, NEWS_API_KEY
from app.db.session import get_db

with get_db() as db:
    ingest = IngestionService(api_key = NEWS_API_KEY, api_url = NEWS_API_URL, db = db)
    ingest.run_full_pipeline()