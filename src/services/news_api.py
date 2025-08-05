import aiohttp
from datetime import datetime, timedelta

class NewsAPIWorker:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url


    async def fetch_news(self, query: str, days: int = 1) -> list[dict]:
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        async with aiohttp.ClientSession() as session:
            params = {
                "q": query,
                "from": from_date,
                "sortBy": "publishedAt",
                "apiKey": self.api_key,
                "language": "ru",
            }

            async with session.get(self.base_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                articles = []
                for article in data.get("articles", []):
                    articles.append(
                        {
                            "title": article["title"],
                            "link": article["url"],
                            "published_at": datetime.strptime(
                                article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                            ),
                            "source": article["source"]["name"],
                            "content": article.get("description", "")
                            + " "
                            + article.get("content", ""),
                        }
                    )

                return articles
