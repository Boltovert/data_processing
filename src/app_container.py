from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Singleton, Resource

from src.analyzer.polit_analyzator import MentionAnalyzer
from src.services.news_api import NewsAPIWorker
from src.services.rss_parser import RSSParser
from src.settings import settings
from src.core.logger import get_logger
from src.core.postgres import Postgres


class ApplicationContainer(DeclarativeContainer):
    wiring_config: WiringConfiguration = WiringConfiguration(
        modules=[
        ]
    )

    logger = Singleton(get_logger)
    postgres = Resource(Postgres.resource(), uri=settings.postgres.uri)

    news_api = Singleton(NewsAPIWorker, api_key=settings.news.api_key, base_url=settings.news.base_url)
    rss_parser = Singleton(RSSParser, feed_urls=settings.rss_parser.rss_urls)
    analyzer = Singleton(MentionAnalyzer, rss_parser=rss_parser, news_api=news_api, entities=settings.analyzer.entities)
