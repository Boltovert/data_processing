from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from src.core.postgres import Postgres
from src.models import Article, PoliticalEntity, Mention
import pandas as pd


class AnalyzerRepository:
    def __init__(self, postgres: Postgres):
        self.postgres = postgres

    async def save_analysis_results(self, df: pd.DataFrame) -> int:
        async with self.postgres(f"{self.__class__.__name__}.save_analysis_results") as session:
            count = 0
            for record in df.to_dict("records"):
                article = await self._get_or_create_article(session, record)
                entity = await self._get_or_create_entity(session, record["entity"])
                await self._create_or_update_mention(
                    session, article, entity, record
                )
                count += 1

            await session.commit()
            return count

    async def get_mentions_stats(self, days: int = 7) -> list[dict]:
        async with self.postgres(f"{self.__class__.__name__}.get_mentions_stats") as session:
            result = await session.execute(
                select(
                    PoliticalEntity.name,
                    Article.source,
                    func.sum(Mention.count).label("total_mentions"),
                )
                .join(Mention.entity)
                .join(Mention.article)
                .where(Article.published_at >= datetime.now() - timedelta(days=days))
                .group_by(PoliticalEntity.name, Article.source)
            )
            return [
                {
                    "entity": row.name,
                    "source": row.source,
                    "total_mentions": row.total_mentions,
                }
                for row in result.all()
            ]

    @staticmethod
    async def _get_or_create_article(
        session: AsyncSession, record: dict
    ) -> Article:
        result = await session.execute(
            select(Article).where(Article.content_hash == record["content_hash"])
        )
        article = result.scalar_one_or_none()

        if not article:
            article = Article(
                title=record["title"],
                url=record["article_url"],
                content=record.get("content", ""),
                published_at=record["date"],
                source=record["source"],
                content_hash=record["content_hash"],
            )
            session.add(article)
            await session.flush()

        return article

    @staticmethod
    async def _get_or_create_entity(
        session: AsyncSession, entity_name: str
    ) -> PoliticalEntity:
        result = await session.execute(
            select(PoliticalEntity).where(PoliticalEntity.name == entity_name)
        )
        entity = result.scalar_one_or_none()

        if not entity:
            entity = PoliticalEntity(name=entity_name)
            session.add(entity)
            await session.flush()

        return entity

    @staticmethod
    async def _create_or_update_mention(
        session: AsyncSession,
        article: Article,
        entity: PoliticalEntity,
        record: dict,
    ) -> None:
        result = await session.execute(
            select(Mention).where(
                and_(Mention.article_id == article.id, Mention.entity_id == entity.id)
            )
        )
        mention = result.scalar_one_or_none()

        if mention:
            mention.count += record["count"]
        else:
            mention = Mention(
                article_id=article.id,
                entity_id=entity.id,
                count=record["count"],
            )
            session.add(mention)
