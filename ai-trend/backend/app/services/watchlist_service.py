import json
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.daily_metric import DailyMetric
from app.models.repository import Repository
from app.services.github_service import GitHubService


class WatchlistService:
    def __init__(self) -> None:
        self.github = GitHubService()

    async def create_or_get_repository(self, db: Session, repo_url: str) -> Repository:
        owner, repo = self.github.parse_repo_url(repo_url)
        full_name = f"{owner}/{repo}"
        repository = db.scalar(select(Repository).where(Repository.full_name == full_name))
        payload = await self.github.fetch_repo(owner, repo)

        if repository is None:
            repository = Repository(
                owner=payload["owner"]["login"],
                name=payload["name"],
                full_name=payload["full_name"],
                repo_url=payload["html_url"],
                description=payload.get("description"),
                language=payload.get("language"),
                default_branch=payload.get("default_branch"),
                stars_current=payload.get("stargazers_count", 0),
                forks_current=payload.get("forks_count", 0),
                subscribers_current=payload.get("subscribers_count", 0),
                open_issues_current=payload.get("open_issues_count", 0),
                topics_json=json.dumps(payload.get("topics", []), ensure_ascii=False),
            )
            db.add(repository)
            db.flush()
        else:
            repository.repo_url = payload["html_url"]
            repository.description = payload.get("description")
            repository.language = payload.get("language")
            repository.default_branch = payload.get("default_branch")
            repository.stars_current = payload.get("stargazers_count", 0)
            repository.forks_current = payload.get("forks_count", 0)
            repository.subscribers_current = payload.get("subscribers_count", 0)
            repository.open_issues_current = payload.get("open_issues_count", 0)
            repository.topics_json = json.dumps(payload.get("topics", []), ensure_ascii=False)
            repository.updated_at = datetime.now(timezone.utc)

        pushed_at = payload.get("pushed_at")
        metric = db.scalar(
            select(DailyMetric).where(
                DailyMetric.repository_id == repository.id,
                DailyMetric.metric_date == date.today(),
            )
        )
        if metric is None:
            metric = DailyMetric(
                repository_id=repository.id,
                metric_date=date.today(),
            )
            db.add(metric)

        metric.stars = payload.get("stargazers_count", 0)
        metric.forks = payload.get("forks_count", 0)
        metric.subscribers = payload.get("subscribers_count", 0)
        metric.open_issues = payload.get("open_issues_count", 0)
        metric.pushed_at = datetime.fromisoformat(pushed_at.replace("Z", "+00:00")) if pushed_at else None
        metric.raw_payload_json = json.dumps(payload, ensure_ascii=False)

        db.commit()
        db.refresh(repository)
        return repository

    def list_repositories(self, db: Session) -> list[Repository]:
        stmt = select(Repository).order_by(Repository.updated_at.desc())
        return list(db.scalars(stmt).all())

    def get_repository(self, db: Session, repo_id: int) -> Repository | None:
        return db.scalar(select(Repository).where(Repository.id == repo_id))


watchlist_service = WatchlistService()
