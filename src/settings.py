import os

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    reload: bool = False
    public_url: str


class PostgresSettings(BaseSettings):
    host: str
    port: int = 5432
    db: str
    user: str
    password: str

    @property
    def uri(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@" f"{self.host}:{self.port}/{self.db}"


class NewsSettings(BaseSettings):
    api_key: str
    base_url: str = "https://newsapi.org/v2/everything"


class RssParserSettings(BaseSettings):
    rss_urls: list[str] = ["https://lenta.ru/rss/news", "https://habr.com/ru/rss/all/all/"]


class AnalyzerSettings(BaseSettings):
    entities: list[str] = [
        "Путин",
        "Putin",
        "Единая Россия",
        "Трамп",
        "Trump",
    ]

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    log_level: str = "warning"
    env: str = "local"
    debug: bool = False

    server: ServerSettings
    postgres: PostgresSettings
    news: NewsSettings
    rss_parser: RssParserSettings = RssParserSettings()
    analyzer: AnalyzerSettings = AnalyzerSettings()

try:
    settings = AppSettings(_env_file=os.getenv("ENV_FILE"))
except ValidationError as e:
    raise e
