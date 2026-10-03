"""加载 resume.md 与 job-infos/ 下的岗位 JD。"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESUME_PATH = BASE_DIR / "resume.md"
JOB_DIR = BASE_DIR / "job-infos"


def load_resume() -> str:
    return RESUME_PATH.read_text(encoding="utf-8")


def load_jobs() -> list[dict]:
    """按文件名排序返回岗位列表，每项为 {id, title, text}。

    id 取文件名前缀（如 "01"），title 取前缀之后的部分（如 "Linux软件开发工程师"）。
    """
    jobs = []
    for path in sorted(JOB_DIR.glob("*.md")):
        job_id, _, title = path.stem.partition("-")
        jobs.append(
            {
                "id": job_id,
                "title": title or path.stem,
                "text": path.read_text(encoding="utf-8"),
            }
        )
    return jobs
