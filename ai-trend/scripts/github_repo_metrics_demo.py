import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def parse_repo_url(repo_url: str) -> tuple[str, str]:
    repo_url = repo_url.strip()
    if not repo_url:
        raise ValueError("GitHub 仓库地址不能为空")

    if not repo_url.startswith(("http://", "https://")):
        repo_url = f"https://{repo_url}"

    parsed = urlparse(repo_url)
    if parsed.netloc not in {"github.com", "www.github.com"}:
        raise ValueError("请输入 github.com 的仓库地址，例如 https://github.com/langgenius/dify")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError("仓库地址格式不正确，至少需要 owner/repo")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo


def fetch_repo_metrics(owner: str, repo: str) -> dict:
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-trend-demo",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    request = Request(api_url, headers=headers)
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def print_metrics(data: dict) -> None:
    metrics = {
        "full_name": data.get("full_name"),
        "html_url": data.get("html_url"),
        "description": data.get("description"),
        "language": data.get("language"),
        "topics": data.get("topics", []),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "watchers_count_api": data.get("watchers_count"),
        "subscribers_count_real_watchers": data.get("subscribers_count"),
        "open_issues": data.get("open_issues_count"),
        "default_branch": data.get("default_branch"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "pushed_at": data.get("pushed_at"),
        "size_kb": data.get("size"),
        "archived": data.get("archived"),
        "disabled": data.get("disabled"),
        "license": (data.get("license") or {}).get("spdx_id"),
    }

    print("\n当前仓库可直接获取的关键信息:\n")
    for key, value in metrics.items():
        print(f"- {key}: {value}")

    print("\n说明:")
    print("- `stargazers_count` 是 star 总数")
    print("- `forks_count` 是 fork 总数")
    print("- `watchers_count` 在 GitHub API 里通常等同于 stars，别把它当真实 watch 数")
    print("- `subscribers_count` 更接近真正的 watch/订阅人数")


def main() -> None:
    repo_url = input("请输入 GitHub 仓库地址: ").strip()
    try:
        owner, repo = parse_repo_url(repo_url)
        data = fetch_repo_metrics(owner, repo)
        print_metrics(data)
    except ValueError as exc:
        print(f"输入错误: {exc}")
        sys.exit(1)
    except HTTPError as exc:
        if exc.code == 404:
            print("请求失败: 仓库不存在，或者仓库名称/地址写错了")
        elif exc.code == 403:
            print("请求失败: GitHub API 被限流了，建议设置环境变量 GITHUB_TOKEN 后重试")
        else:
            print(f"请求失败: HTTP {exc.code}")
        sys.exit(1)
    except URLError as exc:
        print(f"网络错误: {exc.reason}")
        sys.exit(1)


if __name__ == "__main__":
    main()
