from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dashboard import router as dashboard_router
from app.api.repos import router as repos_router
from app.api.watchlist import router as watchlist_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import DailyMetric, Repository
from app.services.watchlist_service import watchlist_service

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    sqlite_path = settings.sqlite_path
    if sqlite_path is not None:
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine, tables=[Repository.__table__, DailyMetric.__table__])

    async def scheduled_job() -> None:
        db = SessionLocal()
        try:
            repositories = watchlist_service.list_repositories(db)
            for repository in repositories:
                await watchlist_service.create_or_get_repository(db, repository.repo_url)
        finally:
            db.close()

    scheduler.add_job(
        scheduled_job,
        "cron",
        hour=2,
        minute=0,
        id="collect_metrics",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(watchlist_router, prefix=settings.api_prefix)
app.include_router(repos_router, prefix=settings.api_prefix)
app.include_router(dashboard_router, prefix=settings.api_prefix)


@app.get("/")
def healthcheck() -> dict:
    return {"status": "ok", "service": settings.app_name}
