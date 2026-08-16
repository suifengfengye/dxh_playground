from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    repo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    default_branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stars_current: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    forks_current: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    subscribers_current: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    open_issues_current: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    topics_json: Mapped[str] = mapped_column(Text(), default="[]", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )

    metrics: Mapped[list["DailyMetric"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
    )
