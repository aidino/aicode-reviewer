from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db_session
from ..services.repository_service import add_repository_with_metadata, get_user_repositories
from .schemas.repository_schemas import AddRepositoryRequest, RepositoryResponse, RepositoryListResponse
from ..auth.utils import get_current_user
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repositories", tags=["repositories"])

@router.get("/", response_model=RepositoryListResponse)
def list_user_repositories(
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """
    Lấy danh sách repositories của user hiện tại.
    """
    logger.info(f"📋 Listing repositories for user {current_user.id}")
    
    try:
        repositories = get_user_repositories(db=db, user_id=current_user.id)
        
        # Convert to response format
        repository_responses = []
        total_cache_size = 0
        cached_count = 0
        
        for repo in repositories:
            repo_response = RepositoryResponse(
                id=repo.id,
                name=repo.name,
                url=repo.url,
                description=repo.description,
                avatar_url=repo.avatar_url,
                language=repo.language,
                default_branch=repo.default_branch,
                is_private=repo.is_private,
                stars=repo.stars,
                forks=repo.forks,
                owner_id=repo.owner_id,
                created_at=repo.created_at,
                updated_at=repo.updated_at,
                last_synced_at=repo.last_synced_at,
                cached_path=repo.cached_path,
                last_commit_hash=repo.last_commit_hash,
                cache_expires_at=repo.cache_expires_at,
                cache_size_mb=repo.cache_size_mb,
                auto_sync_enabled=repo.auto_sync_enabled,
            )
            repository_responses.append(repo_response)
            
            # Calculate summary statistics
            if repo.cached_path:
                cached_count += 1
                total_cache_size += repo.cache_size_mb or 0
        
        # Generate summary statistics
        summary = {
            "total_repositories": len(repositories),
            "cached_repositories": cached_count,
            "total_cache_size_mb": total_cache_size,
            "languages": {},
            "private_count": sum(1 for repo in repositories if repo.is_private),
            "public_count": sum(1 for repo in repositories if not repo.is_private),
        }
        
        # Count by languages
        for repo in repositories:
            if repo.language:
                summary["languages"][repo.language] = summary["languages"].get(repo.language, 0) + 1
        
        response = RepositoryListResponse(
            repositories=repository_responses,
            total_count=len(repositories),
            summary=summary
        )
        
        logger.info(f"✅ Returning {len(repositories)} repositories for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error listing repositories for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list repositories: {str(e)}")

@router.post("/", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def add_repository(
    request: AddRepositoryRequest,
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """
    Add a new repository by URL. Backend will fetch metadata automatically.
    """
    logger.info(f"Adding repository: {request.repo_url} for user {current_user.id}")
    logger.info(f"Access token provided: {'Yes' if request.access_token else 'No'}")
    
    try:
        repo = add_repository_with_metadata(
            db=db,
            repo_url=request.repo_url,
            user_id=current_user.id,
            access_token=request.access_token
        )
        
        # Determine if this was an update or new creation
        if repo.get('_updated'):
            logger.info(f"Repository updated successfully: {repo['name']} (ID: {repo['id']})")
        elif repo.get('_created'):
            logger.info(f"Repository created successfully: {repo['name']} (ID: {repo['id']})")
        else:
            logger.info(f"Repository processed successfully: {repo['name']} (ID: {repo['id']})")
        
        # Clean up internal flags before returning
        repo.pop('_updated', None)
        repo.pop('_created', None)
        
        return repo
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid repository URL: {str(e)}")
    except RuntimeError as e:
        error_msg = str(e)
        logger.error(f"Runtime error: {error_msg}")
        
        # Provide more specific error messages for common issues
        if "authentication failed" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid access token or insufficient permissions"
            )
        elif "repository not found" in error_msg.lower():
            raise HTTPException(
                status_code=404,
                detail="Repository not found: Check URL or repository permissions"
            )
        elif "permission denied" in error_msg.lower():
            raise HTTPException(
                status_code=403,
                detail="Permission denied: Repository is private and requires valid access token"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Clone failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 