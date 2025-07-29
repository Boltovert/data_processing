import logging
import pandas as pd
from datetime import datetime, date
from hashlib import md5

from fastapi import HTTPException
from starlette import status

from src.analyzer.repository import AnalyzerRepository
from src.services.news_api import NewsAPIWorker
from src.services.rss_parser import RSSParser

logger = logging.getLogger(__name__)


class MentionAnalyzer:
    def __init__(
        self,
        repository: AnalyzerRepository,
        rss_parser: RSSParser,
        news_api: NewsAPIWorker,
        entities: list[str],
    ):
        self.repository = repository
        self.rss_parser = rss_parser
        self.news_api = news_api
        self.entities = self._normalize_entities(entities)

    @staticmethod
    def _normalize_entities(entities: list[str]) -> list[str]:
        return [e.strip().lower() for e in entities if e.strip()]

    async def fetch_all_articles(self, days: int = 1) -> list[dict]:
        if not self.entities:
            logger.warning("No entities provided for article fetching")
            return []

        news_articles = await self._fetch_news_articles(days)
        rss_articles = await self._fetch_rss_articles()

        all_articles = news_articles + rss_articles
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles

    async def _fetch_news_articles(self, days: int) -> list[dict]:
        articles = []
        for entity in self.entities:
            try:
                news = await self.news_api.fetch_news(query=entity, days=days)
                articles.extend(news)
                logger.debug(f"Fetched {len(news)} articles for entity: {entity}")
            except Exception as e:
                logger.warning(f"Failed to fetch news for entity {entity}: {str(e)}")
        return articles

    async def _fetch_rss_articles(self) -> list[dict]:
        try:
            rss_articles = await self.rss_parser.fetch_news()
            logger.debug(f"Fetched {len(rss_articles)} RSS articles")
            return rss_articles
        except Exception as e:
            logger.warning(f"Failed to fetch RSS articles: {str(e)}")
            return []

    async def analyze(self, days: int = 1) -> pd.DataFrame:
        try:
            articles = await self.fetch_all_articles(days=days)

            if not articles:
                logger.warning("No articles to analyze")
                return pd.DataFrame()

            data = []
            processed_urls = set()

            for article in articles:
                try:
                    if not article.get("title") or not article.get("content"):
                        continue

                    article_url = article.get("url", "")
                    if article_url in processed_urls:
                        continue
                    processed_urls.add(article_url)

                    full_text = f"{article['title']} {article['content']}".lower()
                    article_date = self._parse_date(article.get("published_at"))
                    source = article.get("source", "unknown")
                    content_hash = self._generate_content_hash(full_text)

                    for entity in self.entities:
                        count = full_text.count(entity)
                        if count > 0:
                            start_pos = full_text.find(entity)
                            snippet = self._get_snippet(full_text, start_pos, entity)

                            data.append(
                                {
                                    "date": article_date,
                                    "entity": entity,
                                    "count": count,
                                    "source": source,
                                    "snippet": snippet,
                                    "article_url": article_url,
                                    "title": article["title"],
                                    "content_hash": content_hash,
                                }
                            )

                except Exception as e:
                    logger.warning(f"Failed to process article: {str(e)}")
                    continue

            df = pd.DataFrame(data)

            if not df.empty:
                try:
                    await self.repository.save_analysis_results(df)
                    logger.info(f"Successfully saved {len(df)} mentions")
                except Exception as e:
                    logger.error(f"Failed to save analysis results: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to save analysis results",
                    )
            else:
                logger.info("No mentions found in articles")

            return df

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analysis failed",
            )

    @staticmethod
    def _parse_date(date_obj) -> date | None:
        if isinstance(date_obj, date):
            return date_obj
        if isinstance(date_obj, datetime):
            return date_obj.date()
        try:
            return pd.to_datetime(date_obj).date()
        except (ValueError, TypeError):
            return datetime.now().date()


    @staticmethod
    def _generate_content_hash(text: str) -> str:
        return md5(text.strip().encode("utf-8")).hexdigest()

    @staticmethod
    def _get_snippet(text: str, pos: int, entity: str, window: int = 50) -> str:
        start = max(0, pos - window)
        end = min(len(text), pos + len(entity) + window)
        snippet = text[start:end]
        return snippet.replace(entity, f"[{entity}]").strip()
