import re
import tempfile
import shutil
import os
from git import Repo, GitCommandError
from sqlalchemy.orm import Session
from ..models import Project
from datetime import datetime, timezone
from typing import Tuple, List
import requests
import logging

# Import new services
from .token_manager import TokenManager
from .repository_cache_service import RepositoryCacheService

logger = logging.getLogger(__name__)

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
    🚨 DEPRECATED: Use RepositoryCacheService.get_or_clone_repository() instead.
    Clone repo về thư mục tạm, trả về path. Nếu use_ssh=True, chuyển sang dạng SSH URL.
    """
    logger.warning("🚨 Using deprecated clone_repository function. Consider using RepositoryCacheService.")
    
    tmp_dir = tempfile.mkdtemp(prefix="repo_clone_")
    clone_url = repo_url
    if access_token:
        # Clone qua HTTPS với token (PAT) - GitHub format
        # Format: https://token@github.com/owner/repo.git
        if "github.com" in repo_url:
            clone_url = repo_url.replace("https://", f"https://{access_token}@")
            if not clone_url.endswith('.git'):
                clone_url += '.git'
        else:
            # For other platforms, use older format
            clone_url = repo_url.replace("https://", f"https://{access_token}:x-oauth-basic@")
    elif use_ssh:
        m = re.match(r"https?://github.com/([^/]+)/([^/.]+)", repo_url)
        if m:
            owner, repo = m.group(1), m.group(2)
            clone_url = f"git@github.com:{owner}/{repo}.git"
    
    print(f"🔄 Attempting to clone: {repo_url}")
    print(f"🔑 Using access token: {'Yes' if access_token else 'No'}")
    print(f"🌐 Clone URL format: {clone_url[:50]}...")  # Only show first 50 chars for security
    
    try:
        Repo.clone_from(clone_url, tmp_dir)
        print(f"✅ Clone successful to: {tmp_dir}")
        return tmp_dir
    except GitCommandError as e:
        print(f"❌ Clone failed: {e}")
        shutil.rmtree(tmp_dir)
        
        # Parse error message để cung cấp thông báo cụ thể
        error_str = str(e).lower()
        if "403" in error_str and "write access to repository not granted" in error_str:
            raise RuntimeError("Permission denied: Token không có quyền truy cập repository này. Hãy kiểm tra: 1) Token có scope 'repo' không? 2) Token có expired không? 3) User sở hữu token có quyền truy cập repo không?")
        elif "404" in error_str or "repository not found" in error_str:
            raise RuntimeError("Repository not found: URL không đúng hoặc repository không tồn tại")
        elif "authentication failed" in error_str or "401" in error_str:
            raise RuntimeError("Authentication failed: Token không hợp lệ hoặc đã expired")
        elif "fatal: could not read username" in error_str:
            raise RuntimeError("Authentication required: Repository là private, cần Personal Access Token")
        else:
            raise RuntimeError(f"Clone repo thất bại: {e}")

def add_repository_with_metadata(db: Session, repo_url: str, user_id: int, access_token: str = None) -> dict:
    """
    🆕 Smart Repository Management:
    Thêm repository mới với smart caching và secure token storage.
    - Lưu PAT token được encrypt an toàn
    - Cache source code với intelligent sync
    - Update metadata khi repository đã tồn tại cho user này
    """
    repo_url = str(repo_url)  # Đảm bảo luôn là string (fix lỗi HttpUrl)
    
    repo_type, owner, repo_name = detect_repository_type(repo_url)
    
    # Initialize services
    token_manager = TokenManager()
    cache_service = RepositoryCacheService()
    
    # Check if repository already exists FOR THIS USER
    existing_project = db.query(Project).filter(
        Project.url == repo_url,
        Project.owner_id == user_id
    ).first()
    
    repo_path = None
    try:
        if existing_project:
            logger.info(f"📝 Repository already exists for user {user_id}: {existing_project.name}")
            
            # Update/store token if provided
            if access_token:
                token_manager.store_token(existing_project, access_token)
                logger.info(f"🔑 Updated token for existing repository: {existing_project.name}")
            
            # Try to get repository from cache or clone with stored token
            try:
                repo_path = cache_service.get_or_clone_repository(existing_project, db)
                logger.info(f"✅ Got repository from cache: {repo_path}")
            except Exception as cache_error:
                logger.warning(f"Cache failed, using temporary clone: {cache_error}")
                # Fallback to temporary clone for metadata only
                stored_token = token_manager.get_token(existing_project)
                repo_path = clone_repository(repo_url, access_token=stored_token or access_token)
        else:
            logger.info(f"➕ Adding new repository for user {user_id}: {repo_name}")
            
            # For new repositories, use temporary clone first to get metadata
            repo_path = clone_repository(repo_url, access_token=access_token)
        
        # 2. Lấy metadata
        if repo_type == "github":
            try:
                meta = fetch_github_metadata(owner, repo_name)
            except Exception:
                meta = parse_local_metadata(repo_path)
        else:
            meta = parse_local_metadata(repo_path)
        
        now = datetime.now(timezone.utc)
        
        if existing_project:
            # 3a. Update existing repository metadata
            logger.info(f"📝 Updating metadata for: {existing_project.name}")
            existing_project.name = meta["name"]
            existing_project.description = meta["description"]
            existing_project.avatar_url = meta["avatar_url"]
            existing_project.language = meta["language"]
            existing_project.default_branch = meta["default_branch"]
            existing_project.is_private = meta["is_private"]
            existing_project.stars = meta["stars"]
            existing_project.forks = meta["forks"]
            existing_project.last_synced_at = now
            existing_project.updated_at = now
            
            db.commit()
            db.refresh(existing_project)
            
            # Set up smart cache for future use if not already cached
            if not existing_project.is_cache_valid:
                try:
                    cache_path = cache_service.get_or_clone_repository(existing_project, db)
                    logger.info(f"🗂️ Set up cache for repository: {cache_path}")
                except Exception as e:
                    logger.warning(f"Could not set up cache: {e}")
            
            # Return updated project data
            return {
                "id": existing_project.id,
                "name": existing_project.name,
                "url": existing_project.url,
                "description": existing_project.description,
                "avatar_url": existing_project.avatar_url,
                "language": existing_project.language,
                "default_branch": existing_project.default_branch,
                "is_private": existing_project.is_private,
                "stars": existing_project.stars,
                "forks": existing_project.forks,
                "owner_id": existing_project.owner_id,
                "created_at": existing_project.created_at,
                "updated_at": existing_project.updated_at,
                "last_synced_at": existing_project.last_synced_at,
                "_updated": True  # Flag to indicate this was an update
            }
        else:
            # 3b. Create new repository
            logger.info(f"➕ Creating new repository: {meta['name']}")
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
            
            # Store token if provided
            if access_token:
                token_manager.store_token(project, access_token)
                db.commit()
                logger.info(f"🔑 Stored token for new repository: {project.name}")
            
            # Set up smart cache
            try:
                cache_path = cache_service.get_or_clone_repository(project, db)
                logger.info(f"🗂️ Set up cache for new repository: {cache_path}")
            except Exception as e:
                logger.warning(f"Could not set up cache for new repository: {e}")
            
            # Return new project data
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
                "_created": True  # Flag to indicate this was a new creation
            }
    finally:
        # Clean up temporary directory if it was used
        if repo_path and repo_path.startswith(tempfile.gettempdir()):
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
                logger.debug(f"🗑️ Cleaned up temporary directory: {repo_path}")

def get_repository_for_scan(project: Project, db: Session) -> str:
    """
    🆕 Get repository path for scanning with smart cache.
    Returns cached path if available, otherwise clones fresh.
    
    Args:
        project: Project instance
        db: Database session
        
    Returns:
        str: Path to repository directory
    """
    cache_service = RepositoryCacheService()
    
    try:
        repo_path = cache_service.get_or_clone_repository(project, db)
        logger.info(f"🔍 Repository ready for scan: {project.name} -> {repo_path}")
        return repo_path
    except Exception as e:
        logger.error(f"Failed to get repository for scan: {project.name}: {e}")
        raise RuntimeError(f"Cannot prepare repository for scan: {str(e)}")

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

def get_user_repositories(db: Session, user_id: int) -> List[Project]:
    """
    Lấy danh sách repositories của user từ database.
    
    Args:
        db: Database session
        user_id: ID của user
        
    Returns:
        List[Project]: Danh sách repositories của user
    """
    logger.info(f"📋 Getting repositories for user {user_id}")
    
    repositories = db.query(Project).filter(
        Project.owner_id == user_id
    ).order_by(Project.updated_at.desc()).all()
    
    logger.info(f"✅ Found {len(repositories)} repositories for user {user_id}")
    return repositories 