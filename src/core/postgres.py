from contextlib import asynccontextmanager
from typing import AsyncIterator

from prometheus_client import Histogram
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)

from src.core.resource import AppResource


class Postgres(AppResource):
    engine: AsyncEngine
    session_maker: async_sessionmaker

    def __init__(
        self,
        uri: str,
        pool_size: int = 10,
        pool_timeout=30,
        pool_recycle=300,
    ):
        self.query_histogram = Histogram("postgres_timings", "", ("metric",))
        self.uri = uri
        self.pool_size = pool_size
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle

    @asynccontextmanager
    async def __call__(
        self,
        metric: str = "postgres",
    ) -> AsyncIterator[AsyncSession]:
        with self.query_histogram.labels(metric=metric).time():
            async with self.session_maker() as con:
                yield con

    async def connect(self) -> None:
        self.engine: AsyncEngine = create_async_engine(
            self.uri,
            pool_size=self.pool_size,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
        )
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            future=True,
            expire_on_commit=False,
        )

    async def disconnect(self) -> None:
        await self.engine.dispose()
