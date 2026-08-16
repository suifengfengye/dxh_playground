from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.watchlist import to_repo_read
from app.db.session import get_db
from app.models.daily_metric import DailyMetric
from app.schemas.metric import DailyMetricRead
from app.schemas.repo import RepositoryRead
from app.services.watchlist_service import watchlist_service

router = APIRouter(prefix="/repos", tags=["repos"])


@router.get("/{repo_id}", response_model=RepositoryRead)
def get_repository(repo_id: int, db: Session = Depends(get_db)) -> RepositoryRead:
    repository = watchlist_service.get_repository(db, repo_id)
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    return to_repo_read(repository)


@router.get("/{repo_id}/metrics", response_model=list[DailyMetricRead])
def get_repository_metrics(repo_id: int, db: Session = Depends(get_db)) -> list[DailyMetricRead]:
    repository = watchlist_service.get_repository(db, repo_id)
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    stmt = (
        select(DailyMetric)
        .where(DailyMetric.repository_id == repo_id)
        .order_by(DailyMetric.metric_date.asc())
    )
    metrics = list(db.scalars(stmt).all())
    return [
        DailyMetricRead(
            metric_date=item.metric_date,
            stars=item.stars,
            forks=item.forks,
            subscribers=item.subscribers,
            open_issues=item.open_issues,
            pushed_at=item.pushed_at,
        )
        for item in metrics
    ]
