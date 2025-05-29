"""
Smart Repository Cache Service
Manages local caching of repository source code with intelligent sync.
"""

import os
import shutil
import logging
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from pathlib import Path
from git import Repo, GitCommandError
from sqlalchemy.orm import Session
from ..models.project_models import Project
from .token_manager import TokenManager

logger = logging.getLogger(__name__)

class RepositoryCacheService:
    """
    Intelligent caching service for repository source code.
    Features:
    - Smart sync based on git commit hash
    - Automatic cache expiration and cleanup
    - Storage quota management
    - Token-based authentication for private repos
    """
    
    def __init__(self, cache_root: str = "/app/cache/repositories"):
        """
        Initialize cache service.
        
        Args:
            cache_root: Root directory for cache storage
        """
        self.cache_root = Path(cache_root)
        self.cache_root.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.max_cache_size_gb = int(os.getenv('MAX_CACHE_SIZE_GB', '10'))
        self.default_cache_ttl_hours = int(os.getenv('DEFAULT_CACHE_TTL_HOURS', '24'))
        
        self.token_manager = TokenManager()
        
        logger.info(f"🗂️ Repository cache initialized at {self.cache_root}")
        logger.info(f"📊 Max cache size: {self.max_cache_size_gb}GB, TTL: {self.default_cache_ttl_hours}h")
    
    def get_or_clone_repository(self, project: Project, db: Session) -> str:
        """
        Get repository path from cache or clone if needed.
        
        Args:
            project: Project instance
            db: Database session for updates
            
        Returns:
            str: Path to repository directory
            
        Raises:
            RuntimeError: If clone/sync fails
        """
        cache_path = self._get_cache_path(project)
        
        try:
            # Check if cache is valid and exists
            if project.is_cache_valid and os.path.exists(cache_path):
                logger.info(f"📂 Using cached repository: {project.name}")
                
                # Check if we need to sync
                if self._needs_sync(project):
                    logger.info(f"🔄 Syncing repository: {project.name}")
                    self._sync_repository(project, cache_path, db)
                
                return cache_path
            else:
                # Cache invalid or missing, clone fresh
                logger.info(f"⬇️ Cloning fresh repository: {project.name}")
                return self._clone_fresh(project, db)
                
        except Exception as e:
            logger.error(f"Failed to get repository {project.name}: {e}")
            # Cleanup broken cache if exists
            if os.path.exists(cache_path):
                shutil.rmtree(cache_path, ignore_errors=True)
                project.cached_path = None
                project.cache_expires_at = None
                db.commit()
            raise RuntimeError(f"Failed to get repository: {str(e)}")
    
    def _get_cache_path(self, project: Project) -> str:
        """Generate cache directory path for project."""
        # Use project ID and URL hash for unique path
        url_hash = hashlib.md5(project.url.encode()).hexdigest()[:8]
        cache_dir_name = f"{project.id}_{project.name}_{url_hash}"
        return str(self.cache_root / cache_dir_name)
    
    def _needs_sync(self, project: Project) -> bool:
        """
        Check if repository needs sync with remote.
        
        Args:
            project: Project instance
            
        Returns:
            bool: True if sync is needed
        """
        if not project.last_commit_hash:
            return True
        
        try:
            # Get remote commit hash
            remote_hash = self._get_remote_commit_hash(project)
            needs_sync = remote_hash != project.last_commit_hash
            
            if needs_sync:
                logger.info(f"🔄 Repository {project.name} needs sync: {project.last_commit_hash[:8]} -> {remote_hash[:8]}")
            
            return needs_sync
            
        except Exception as e:
            logger.warning(f"Could not check remote hash for {project.name}: {e}")
            return True  # Err on the side of syncing
    
    def _get_remote_commit_hash(self, project: Project) -> str:
        """
        Get latest commit hash from remote repository.
        
        Args:
            project: Project instance
            
        Returns:
            str: Latest commit hash
        """
        import requests
        
        # Try GitHub API first (faster)
        if "github.com" in project.url:
            try:
                # Extract owner/repo from URL
                parts = project.url.replace('https://github.com/', '').replace('.git', '').split('/')
                if len(parts) >= 2:
                    owner, repo = parts[0], parts[1]
                    
                    # Try with token if available
                    headers = {}
                    token = self.token_manager.get_token(project)
                    if token:
                        headers['Authorization'] = f'token {token}'
                    
                    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{project.default_branch or 'main'}"
                    resp = requests.get(url, headers=headers, timeout=10)
                    
                    if resp.status_code == 200:
                        return resp.json()['sha']
            except Exception as e:
                logger.debug(f"GitHub API failed for {project.name}: {e}")
        
        # Fallback: use git ls-remote
        return self._get_remote_hash_via_git(project)
    
    def _get_remote_hash_via_git(self, project: Project) -> str:
        """Get remote commit hash using git ls-remote."""
        import subprocess
        
        try:
            clone_url = self._build_clone_url(project)
            
            # Use git ls-remote to get latest commit
            result = subprocess.run(
                ['git', 'ls-remote', clone_url, f'refs/heads/{project.default_branch or "main"}'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                return result.stdout.split('\t')[0]
            else:
                raise RuntimeError(f"git ls-remote failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Failed to get remote hash for {project.name}: {e}")
            raise
    
    def _sync_repository(self, project: Project, cache_path: str, db: Session) -> None:
        """
        Sync existing cached repository with remote.
        
        Args:
            project: Project instance
            cache_path: Path to cached repository
            db: Database session
        """
        try:
            repo = Repo(cache_path)
            
            # Update remote URL with current token if available
            token = self.token_manager.get_token(project)
            if token:
                clone_url = self._build_clone_url(project, token)
                origin = repo.remotes.origin
                origin.set_url(clone_url)
            
            # Pull latest changes
            origin = repo.remotes.origin
            origin.pull()
            
            # Update project metadata
            new_hash = repo.head.commit.hexsha
            project.last_commit_hash = new_hash
            project.last_synced_at = datetime.now(timezone.utc)
            
            # Update cache expiration
            project.cache_expires_at = datetime.now(timezone.utc) + timedelta(hours=self.default_cache_ttl_hours)
            
            db.commit()
            logger.info(f"✅ Synced repository {project.name} to {new_hash[:8]}")
            
        except Exception as e:
            logger.error(f"Sync failed for {project.name}: {e}")
            # Remove broken cache and fall back to fresh clone
            shutil.rmtree(cache_path, ignore_errors=True)
            project.cached_path = None
            project.cache_expires_at = None
            db.commit()
            raise
    
    def _clone_fresh(self, project: Project, db: Session) -> str:
        """
        Clone repository fresh to cache.
        
        Args:
            project: Project instance  
            db: Database session
            
        Returns:
            str: Path to cloned repository
        """
        cache_path = self._get_cache_path(project)
        
        # Remove existing cache if any
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
        
        try:
            # Get clone URL with token
            token = self.token_manager.get_token(project)
            clone_url = self._build_clone_url(project, token)
            
            logger.info(f"🔄 Cloning {project.name} to {cache_path}")
            
            # Clone repository
            repo = Repo.clone_from(clone_url, cache_path)
            
            # Update project metadata
            commit_hash = repo.head.commit.hexsha
            cache_size = self._calculate_directory_size(cache_path)
            
            project.cached_path = cache_path
            project.last_commit_hash = commit_hash
            project.cache_expires_at = datetime.now(timezone.utc) + timedelta(hours=self.default_cache_ttl_hours)
            project.cache_size_mb = cache_size
            project.last_synced_at = datetime.now(timezone.utc)
            
            db.commit()
            
            logger.info(f"✅ Cloned {project.name}: {commit_hash[:8]}, {cache_size}MB")
            return cache_path
            
        except GitCommandError as e:
            logger.error(f"Clone failed for {project.name}: {e}")
            if os.path.exists(cache_path):
                shutil.rmtree(cache_path, ignore_errors=True)
            
            # Clean project cache info
            project.cached_path = None
            project.cache_expires_at = None
            project.cache_size_mb = 0
            db.commit()
            
            raise RuntimeError(f"Failed to clone repository: {str(e)}")
    
    def _build_clone_url(self, project: Project, token: Optional[str] = None) -> str:
        """Build clone URL with optional token authentication."""
        clone_url = project.url
        
        if token and "github.com" in project.url:
            # GitHub format: https://token@github.com/owner/repo.git
            clone_url = project.url.replace("https://", f"https://{token}@")
            if not clone_url.endswith('.git'):
                clone_url += '.git'
        elif token:
            # Generic format for other platforms
            clone_url = project.url.replace("https://", f"https://{token}:x-oauth-basic@")
        
        return clone_url
    
    def _calculate_directory_size(self, path: str) -> int:
        """Calculate directory size in MB."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    pass
        return int(total_size / (1024 * 1024))  # Convert to MB
    
    def cleanup_expired_cache(self, db: Session) -> int:
        """
        Remove expired cache directories.
        
        Args:
            db: Database session
            
        Returns:
            int: Number of cache directories cleaned up
        """
        expired_projects = db.query(Project).filter(
            Project.cache_expires_at < datetime.now(timezone.utc),
            Project.cached_path.isnot(None)
        ).all()
        
        count = 0
        for project in expired_projects:
            if project.cached_path and os.path.exists(project.cached_path):
                shutil.rmtree(project.cached_path, ignore_errors=True)
                logger.info(f"🗑️ Removed expired cache for {project.name}")
            
            project.cached_path = None
            project.cache_expires_at = None
            project.cache_size_mb = 0
            count += 1
        
        if count > 0:
            db.commit()
            logger.info(f"🧹 Cleaned up {count} expired caches")
        
        return count
    
    def manage_storage_quota(self, db: Session) -> int:
        """
        Manage storage quota by removing LRU caches.
        
        Args:
            db: Database session
            
        Returns:
            int: Number of caches removed
        """
        # Calculate total cache size
        total_size_mb = db.query(Project).filter(
            Project.cached_path.isnot(None)
        ).with_entities(db.func.sum(Project.cache_size_mb)).scalar() or 0
        
        max_size_mb = self.max_cache_size_gb * 1024
        
        if total_size_mb <= max_size_mb:
            return 0  # Under quota
        
        logger.warning(f"📊 Cache over quota: {total_size_mb}MB > {max_size_mb}MB")
        
        # Remove least recently used caches
        lru_projects = db.query(Project).filter(
            Project.cached_path.isnot(None)
        ).order_by(Project.last_synced_at.asc()).all()
        
        removed_count = 0
        for project in lru_projects:
            if total_size_mb <= max_size_mb * 0.8:  # Target 80% of quota
                break
            
            if project.cached_path and os.path.exists(project.cached_path):
                shutil.rmtree(project.cached_path, ignore_errors=True)
                logger.info(f"🗑️ Removed LRU cache for {project.name} ({project.cache_size_mb}MB)")
                
                total_size_mb -= project.cache_size_mb
                project.cached_path = None
                project.cache_expires_at = None
                project.cache_size_mb = 0
                removed_count += 1
        
        if removed_count > 0:
            db.commit()
            logger.info(f"🧹 Removed {removed_count} caches for storage quota")
        
        return removed_count 