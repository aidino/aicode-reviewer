"""
Background Jobs for Repository Cache Management
Handles cleanup, auto-sync, and maintenance tasks.
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db_session
from ..models.project_models import Project
from .token_manager import TokenManager
from .repository_cache_service import RepositoryCacheService

logger = logging.getLogger(__name__)

class RepositoryMaintenanceJobs:
    """
    Background maintenance jobs for repository cache and token management.
    """
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.cache_service = RepositoryCacheService()
    
    async def cleanup_expired_cache_job(self) -> dict:
        """
        Background job to clean up expired repository caches.
        
        Returns:
            dict: Cleanup statistics
        """
        logger.info("🧹 Starting expired cache cleanup job")
        
        with next(get_db_session()) as db:
            try:
                # Cleanup expired caches
                cleaned_caches = self.cache_service.cleanup_expired_cache(db)
                
                # Cleanup expired tokens
                cleaned_tokens = self.token_manager.cleanup_expired_tokens(db)
                
                # Manage storage quota
                quota_cleanups = self.cache_service.manage_storage_quota(db)
                
                result = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "cleaned_caches": cleaned_caches,
                    "cleaned_tokens": cleaned_tokens,
                    "quota_cleanups": quota_cleanups,
                    "status": "completed"
                }
                
                logger.info(f"✅ Cleanup job completed: {result}")
                return result
                
            except Exception as e:
                logger.error(f"❌ Cleanup job failed: {e}")
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": str(e),
                    "status": "failed"
                }
    
    async def auto_sync_repositories_job(self, batch_size: int = 10) -> dict:
        """
        Background job to auto-sync repositories that need updates.
        
        Args:
            batch_size: Number of repositories to sync per batch
            
        Returns:
            dict: Sync statistics
        """
        logger.info(f"🔄 Starting auto-sync job (batch size: {batch_size})")
        
        with next(get_db_session()) as db:
            try:
                # Get repositories that need sync
                candidates = db.query(Project).filter(
                    Project.auto_sync_enabled == True,
                    Project.cached_path.isnot(None),
                    # Sync repositories that haven't been synced in the last hour
                    Project.last_synced_at < datetime.now(timezone.utc) - timedelta(hours=1)
                ).order_by(Project.last_synced_at.asc()).limit(batch_size).all()
                
                synced_count = 0
                failed_count = 0
                sync_results = []
                
                for project in candidates:
                    try:
                        logger.info(f"🔄 Auto-syncing repository: {project.name}")
                        
                        # Use cache service to sync
                        repo_path = self.cache_service.get_or_clone_repository(project, db)
                        
                        sync_results.append({
                            "repository": project.name,
                            "status": "synced",
                            "path": repo_path,
                            "commit_hash": project.last_commit_hash[:8] if project.last_commit_hash else None
                        })
                        synced_count += 1
                        
                        # Small delay to avoid overwhelming Git servers
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to sync repository {project.name}: {e}")
                        sync_results.append({
                            "repository": project.name,
                            "status": "failed",
                            "error": str(e)
                        })
                        failed_count += 1
                
                result = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_candidates": len(candidates),
                    "synced_count": synced_count,
                    "failed_count": failed_count,
                    "sync_results": sync_results,
                    "status": "completed"
                }
                
                logger.info(f"✅ Auto-sync job completed: {synced_count} synced, {failed_count} failed")
                return result
                
            except Exception as e:
                logger.error(f"❌ Auto-sync job failed: {e}")
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": str(e),
                    "status": "failed"
                }
    
    async def cache_health_check_job(self) -> dict:
        """
        Background job to check cache health and generate statistics.
        
        Returns:
            dict: Health statistics
        """
        logger.info("🏥 Starting cache health check job")
        
        with next(get_db_session()) as db:
            try:
                # Calculate statistics
                total_projects = db.query(Project).count()
                cached_projects = db.query(Project).filter(Project.cached_path.isnot(None)).count()
                
                total_cache_size = db.query(func.sum(Project.cache_size_mb)).filter(
                    Project.cached_path.isnot(None)
                ).scalar() or 0
                
                projects_with_tokens = db.query(Project).filter(
                    Project.encrypted_access_token.isnot(None)
                ).count()
                
                expired_caches = db.query(Project).filter(
                    Project.cache_expires_at < datetime.now(timezone.utc),
                    Project.cached_path.isnot(None)
                ).count()
                
                expired_tokens = db.query(Project).filter(
                    Project.token_expires_at < datetime.now(timezone.utc),
                    Project.encrypted_access_token.isnot(None)
                ).count()
                
                # Calculate cache efficiency
                cache_efficiency = (cached_projects / total_projects * 100) if total_projects > 0 else 0
                
                result = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "statistics": {
                        "total_projects": total_projects,
                        "cached_projects": cached_projects,
                        "cache_efficiency_percent": round(cache_efficiency, 2),
                        "total_cache_size_mb": total_cache_size,
                        "total_cache_size_gb": round(total_cache_size / 1024, 2),
                        "projects_with_tokens": projects_with_tokens,
                        "expired_caches": expired_caches,
                        "expired_tokens": expired_tokens
                    },
                    "recommendations": [],
                    "status": "completed"
                }
                
                # Add recommendations
                if expired_caches > 0:
                    result["recommendations"].append(f"Run cleanup job - {expired_caches} expired caches found")
                
                if expired_tokens > 0:
                    result["recommendations"].append(f"Token cleanup needed - {expired_tokens} expired tokens found")
                
                if total_cache_size > self.cache_service.max_cache_size_gb * 1024:
                    result["recommendations"].append("Cache size over limit - consider quota management")
                
                if cache_efficiency < 50:
                    result["recommendations"].append("Low cache efficiency - consider increasing TTL")
                
                logger.info(f"🏥 Health check completed: {cache_efficiency:.1f}% efficiency, {total_cache_size}MB cached")
                return result
                
            except Exception as e:
                logger.error(f"❌ Health check job failed: {e}")
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": str(e),
                    "status": "failed"
                }
    
    async def run_maintenance_cycle(self) -> dict:
        """
        Run a full maintenance cycle including all cleanup and sync tasks.
        
        Returns:
            dict: Combined results from all maintenance tasks
        """
        logger.info("🔧 Starting full maintenance cycle")
        
        start_time = datetime.now(timezone.utc)
        
        # Run all maintenance tasks
        cleanup_result = await self.cleanup_expired_cache_job()
        sync_result = await self.auto_sync_repositories_job()
        health_result = await self.cache_health_check_job()
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        result = {
            "timestamp": end_time.isoformat(),
            "duration_seconds": round(duration, 2),
            "cleanup_result": cleanup_result,
            "sync_result": sync_result,
            "health_result": health_result,
            "status": "completed"
        }
        
        logger.info(f"🔧 Maintenance cycle completed in {duration:.2f}s")
        return result

# Singleton instance for background jobs
maintenance_jobs = RepositoryMaintenanceJobs()

# Job scheduling functions (can be used with Celery, APScheduler, etc.)
async def scheduled_cleanup_job():
    """Scheduled cleanup job - run every 6 hours"""
    return await maintenance_jobs.cleanup_expired_cache_job()

async def scheduled_sync_job():
    """Scheduled sync job - run every hour"""
    return await maintenance_jobs.auto_sync_repositories_job()

async def scheduled_health_check():
    """Scheduled health check - run every 4 hours"""
    return await maintenance_jobs.cache_health_check_job()

async def scheduled_full_maintenance():
    """Scheduled full maintenance - run daily"""
    return await maintenance_jobs.run_maintenance_cycle() 