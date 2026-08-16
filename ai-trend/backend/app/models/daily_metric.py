from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DailyMetric(Base):
    __tablename__ = "daily_metrics"
    __table_args__ = (UniqueConstraint("repository_id", "metric_date", name="uq_repo_metric_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"), nullable=False, index=True)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    stars: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    forks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    subscribers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    open_issues: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pushed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_payload_json: Mapped[str] = mapped_column(Text(), default="{}", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    repository: Mapped["Repository"] = relationship(back_populates="metrics")
