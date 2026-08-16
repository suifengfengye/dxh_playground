import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.repo import RepositoryRead
from app.schemas.watchlist import WatchlistCreate
from app.services.watchlist_service import watchlist_service

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


def to_repo_read(repository) -> RepositoryRead:
    return RepositoryRead(
        id=repository.id,
        owner=repository.owner,
        name=repository.name,
        full_name=repository.full_name,
        repo_url=repository.repo_url,
        description=repository.description,
        language=repository.language,
        default_branch=repository.default_branch,
        stars_current=repository.stars_current,
        forks_current=repository.forks_current,
        subscribers_current=repository.subscribers_current,
        open_issues_current=repository.open_issues_current,
        topics=json.loads(repository.topics_json or "[]"),
        is_active=repository.is_active,
        created_at=repository.created_at,
        updated_at=repository.updated_at,
    )


@router.get("", response_model=list[RepositoryRead])
def list_watchlist(db: Session = Depends(get_db)) -> list[RepositoryRead]:
    repositories = watchlist_service.list_repositories(db)
    return [to_repo_read(item) for item in repositories]


@router.post("", response_model=RepositoryRead)
async def create_watchlist_item(
    payload: WatchlistCreate,
    db: Session = Depends(get_db),
) -> RepositoryRead:
    repository = await watchlist_service.create_or_get_repository(db, str(payload.repo_url))
    return to_repo_read(repository)
