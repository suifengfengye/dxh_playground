from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RepositoryRead(BaseModel):
    id: int
    owner: str
    name: str
    full_name: str
    repo_url: str
    description: str | None
    language: str | None
    default_branch: str | None
    stars_current: int
    forks_current: int
    subscribers_current: int
    open_issues_current: int
    topics: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
