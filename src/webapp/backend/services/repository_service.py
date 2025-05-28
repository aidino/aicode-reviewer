import re
import tempfile
import shutil
import os
from git import Repo, GitCommandError
from sqlalchemy.orm import Session
from ..models import Project
from datetime import datetime, timezone
from typing import Tuple
import requests

def detect_repository_type(repo_url: str) -> Tuple[str, str, str]:
    """
    Xác định loại repository (github, gitlab, bitbucket) và trả về (type, owner, repo_name)
    """
    # GitHub
    m = re.match(r"https?://github.com/([^/]+)/([^/.]+)", repo_url)
    if m:
        return ("github", m.group(1), m.group(2))
    # GitLab
    m = re.match(r"https?://gitlab.com/([^/]+)/([^/.]+)", repo_url)
    if m:
        return ("gitlab", m.group(1), m.group(2))
    # Bitbucket
    m = re.match(r"https?://bitbucket.org/([^/]+)/([^/.]+)", repo_url)
    if m:
        return ("bitbucket", m.group(1), m.group(2))
    raise ValueError("Không hỗ trợ repo_url này hoặc URL không hợp lệ")

def clone_repository(repo_url: str, use_ssh: bool = False, access_token: str = None) -> str:
    """
    Clone repo về thư mục tạm, trả về path. Nếu use_ssh=True, chuyển sang dạng SSH URL.
    """
    tmp_dir = tempfile.mkdtemp(prefix="repo_clone_")
    clone_url = repo_url
    if access_token:
        # Clone qua HTTPS với token (PAT)
        clone_url = repo_url.replace("https://", f"https://{access_token}:x-oauth-basic@")
    elif use_ssh:
        m = re.match(r"https?://github.com/([^/]+)/([^/.]+)", repo_url)
        if m:
            owner, repo = m.group(1), m.group(2)
            clone_url = f"git@github.com:{owner}/{repo}.git"
    try:
        Repo.clone_from(clone_url, tmp_dir)
        return tmp_dir
    except GitCommandError as e:
        shutil.rmtree(tmp_dir)
        raise RuntimeError(f"Clone repo thất bại: {e}")

def add_repository_with_metadata(db: Session, repo_url: str, user_id: int, access_token: str = None) -> dict:
    repo_url = str(repo_url)  # Đảm bảo luôn là string (fix lỗi HttpUrl)
    """
    Thêm repository mới: clone repo, lấy metadata, lưu vào DB, trả về dict thông tin repo.
    """
    repo_type, owner, repo_name = detect_repository_type(repo_url)
    use_ssh = False  # Chỉ dùng cho dev đặc biệt
    repo_path = None
    try:
        # 1. Clone repo về thư mục tạm
        repo_path = clone_repository(repo_url, use_ssh=use_ssh, access_token=access_token)
        # 2. Lấy metadata
        if repo_type == "github":
            try:
                meta = fetch_github_metadata(owner, repo_name)
            except Exception:
                meta = parse_local_metadata(repo_path)
        else:
            meta = parse_local_metadata(repo_path)
        # 3. Lưu vào DB
        now = datetime.now(timezone.utc)
        project = Project(
            name=meta["name"],
            url=repo_url,
            description=meta["description"],
            avatar_url=meta["avatar_url"],
            language=meta["language"],
            default_branch=meta["default_branch"],
            is_private=meta["is_private"],
            stars=meta["stars"],
            forks=meta["forks"],
            last_synced_at=now,
            created_at=now,
            updated_at=now,
            owner_id=user_id,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        # 4. Trả về dict thông tin repo
        return {
            "id": project.id,
            "name": project.name,
            "url": project.url,
            "description": project.description,
            "avatar_url": project.avatar_url,
            "language": project.language,
            "default_branch": project.default_branch,
            "is_private": project.is_private,
            "stars": project.stars,
            "forks": project.forks,
            "owner_id": project.owner_id,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "last_synced_at": project.last_synced_at,
        }
    finally:
        if repo_path and os.path.exists(repo_path):
            shutil.rmtree(repo_path)

def fetch_github_metadata(owner: str, repo: str) -> dict:
    """
    Lấy metadata repo từ GitHub API (public info).
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return {
            "name": data.get("name"),
            "description": data.get("description"),
            "avatar_url": data.get("owner", {}).get("avatar_url"),
            "language": data.get("language"),
            "default_branch": data.get("default_branch"),
            "is_private": data.get("private", False),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
        }
    else:
        raise RuntimeError(f"Không lấy được metadata từ GitHub API: {resp.status_code}")

def parse_local_metadata(repo_path: str) -> dict:
    """
    Parse metadata cơ bản từ local repo (README, .git/config).
    """
    name = os.path.basename(repo_path)
    description = None
    readme_path = os.path.join(repo_path, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            description = f.readline().strip()
    # TODO: Parse thêm .git/config nếu cần
    return {
        "name": name,
        "description": description,
        "avatar_url": None,
        "language": None,
        "default_branch": None,
        "is_private": False,
        "stars": 0,
        "forks": 0,
    } 