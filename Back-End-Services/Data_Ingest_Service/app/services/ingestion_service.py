from app.scraper.api_connector import APIConnector
from sqlalchemy.orm import Session

class IngestionService:
    """
    API-only ingestion pipeline:
    API → dedup → normalize → return
    """

    def __init__(self, api_key, api_url, db: Session, db_tname):
        self.api = APIConnector(api_key, api_url)
        self.db = db,
        self.db_tname = db_tname

    def run(self, max_pages = 10, page_size = 20):
        