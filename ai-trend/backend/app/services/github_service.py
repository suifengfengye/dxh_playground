from urllib.parse import urlparse

import httpx

from app.core.config import settings


class GitHubRepoError(ValueError):
    pass


class GitHubService:
    API_BASE = "https://api.github.com"

    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "ai-trend-mvp",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if settings.github_token:
            self.headers["Authorization"] = f"Bearer {settings.github_token}"

    @staticmethod
    def parse_repo_url(repo_url: str) -> tuple[str, str]:
        raw = repo_url.strip()
        if not raw:
            raise GitHubRepoError("GitHub 仓库地址不能为空")
        if not raw.startswith(("http://", "https://")):
            raw = f"https://{raw}"

        parsed = urlparse(raw)
        if parsed.netloc not in {"github.com", "www.github.com"}:
            raise GitHubRepoError("请输入 github.com 的仓库地址")

        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise GitHubRepoError("仓库地址格式必须包含 owner/repo")

        owner, repo = parts[0], parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]
        return owner, repo

    async def fetch_repo(self, owner: str, repo: str) -> dict:
        url = f"{self.API_BASE}/repos/{owner}/{repo}"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers=self.headers)

        if response.status_code == 404:
            raise GitHubRepoError("仓库不存在，或者 owner/repo 写错了")
        if response.status_code == 403:
            raise GitHubRepoError("GitHub API 被限流，请配置 GITHUB_TOKEN")

        response.raise_for_status()
        return response.json()
