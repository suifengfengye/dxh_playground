from pydantic import BaseModel, HttpUrl


class WatchlistCreate(BaseModel):
    repo_url: HttpUrl
