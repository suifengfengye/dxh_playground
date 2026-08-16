from datetime import date, datetime

from pydantic import BaseModel


class DailyMetricRead(BaseModel):
    metric_date: date
    stars: int
    forks: int
    subscribers: int
    open_issues: int
    pushed_at: datetime | None
