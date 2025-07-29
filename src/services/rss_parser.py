import feedparser  # type: ignore

from datetime import datetime

class RSSParser:
    def __init__(self, feed_urls: list[str]):
        self.feed_urls = feed_urls


    async def fetch_news(self) -> list[dict]:
        articles = []
        for url in self.feed_urls:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published_at": datetime(*entry.published_parsed[:6]),
                    "source": url,
                    "content": entry.get("summary", ""),
                })
        return articles
