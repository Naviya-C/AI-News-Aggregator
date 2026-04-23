# app/scraper/article_fetcher.py
import aiohttp # Async HTTP client
import asyncio # Core async framework in Python
from newspaper import Article  


class ArticleFetcher:
    """
    This class is used to extract content cause free api don't provide the fully content.
            Take URLs → fetch HTML → extract article text → return content
            
    Still Under consatruction now yet integrated for production.
    """
    
    HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    }  

    async def fetch_article(self, session, url):
        try:
            async with session.get(url, timeout=10, headers = self.HEADERS) as resp:
                html = await resp.text()

            article = Article(url)
            article.set_html(html)
            article.parse()

            return {
                "url": url,
                "content": article.text
            }

        except Exception:
            return {"url": url, "content": None}

    async def fetch_all(self, urls) -> list[dict]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_article(session, url) for url in urls]
            return await asyncio.gather(*tasks)