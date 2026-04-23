from app.scraper.api_connector import APIConnector
from app.core.config import NEWS_API_KEY, NEWS_API_URL

class IngestionService:
    """
    API-only ingestion pipeline:
    API → dedup → normalize → return
    """

    def __init__(self, api_key, api_url):
        self.api = APIConnector(api_key, api_url)

    def run(self, max_pages=5, page_size=20):
        seen_urls = set()
        all_results = []

        for page in range(1, max_pages + 1):
            batch = self.api.fetch(page=page, page_size=page_size)

            if not batch:
                break
            
            unique_batch = []
            for item in batch:
                url = item.get("url")

                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)
                unique_batch.append(item)

            if not unique_batch:
                continue

            processed = []
            for item in unique_batch:

                summary = item.get("summary")
                content = item.get("content")

                if not summary and not content:
                    continue

                processed.append({
                    "title": item.get("title"),
                    "summary": summary,
                    "content": content,   # keep separate
                    "url": item.get("url"),
                    "source_name": item.get("source_name"),
                    "published_at": item.get("published_at"),
                })

            all_results.extend(processed)

        return all_results
    
x = IngestionService(api_key=NEWS_API_KEY, api_url=NEWS_API_URL)
print(x.run(1, 1))