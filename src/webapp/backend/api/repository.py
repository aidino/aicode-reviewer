from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db_session
from ..services.repository_service import add_repository_with_metadata
from .schemas.repository_schemas import AddRepositoryRequest, RepositoryResponse
from ..auth.utils import get_current_user

router = APIRouter(prefix="/repositories", tags=["repositories"])

@router.post("/", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def add_repository(
    request: AddRepositoryRequest,
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """
    Add a new repository by URL. Backend will fetch metadata automatically.
    """
    try:
        repo = add_repository_with_metadata(
            db=db,
            repo_url=request.repo_url,
            user_id=current_user.id,
            access_token=request.access_token
        )
        return repo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 