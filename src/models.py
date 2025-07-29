from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime, timezone
from src.core.models_base import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    mentions: Mapped[list["Mention"]] = relationship(
        "Mention", back_populates="article", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )

class PoliticalEntity(Base):
    __tablename__ = "political_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[str | None] = mapped_column(String(50))


class Mention(Base):
    __tablename__ = "mentions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("political_entities.id"), nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    article: Mapped["Article"] = relationship("Article", back_populates="mentions", default=None)
    entity: Mapped["PoliticalEntity"] = relationship("PoliticalEntity", default=None)

    __table_args__ = (
        Index("ix_mentions_article_entity", "article_id", "entity_id", unique=True),
    )
