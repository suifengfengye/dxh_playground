from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.repository import Repository

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)) -> dict:
    total_repositories = db.scalar(select(func.count(Repository.id))) or 0
    latest_update = db.scalar(select(func.max(Repository.updated_at)))
    return {
        "total_repositories": total_repositories,
        "latest_update": latest_update,
    }
