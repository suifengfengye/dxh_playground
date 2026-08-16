from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Trend API"
    api_prefix: str = "/api"
    github_token: str | None = None
    database_url: str = "sqlite:///./data/app.db"
    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def sqlite_path(self) -> Path | None:
        if not self.database_url.startswith("sqlite:///"):
            return None
        return Path(self.database_url.removeprefix("sqlite:///"))


settings = Settings()
