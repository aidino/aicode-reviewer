"""
Secure Token Management Service
Handles encryption/decryption of Personal Access Tokens for private repositories.
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from ..models.project_models import Project

logger = logging.getLogger(__name__)

class TokenManager:
    """
    Secure management of PAT tokens with encryption at rest.
    """
    
    def __init__(self):
        """Initialize token manager with encryption key."""
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """
        Get encryption key from environment or create new one.
        
        Returns:
            bytes: Fernet encryption key
        """
        # Try to get key from environment first
        key_env = os.getenv('REPOSITORY_TOKEN_ENCRYPTION_KEY')
        if key_env:
            try:
                return key_env.encode()
            except Exception as e:
                logger.warning(f"Invalid encryption key in environment: {e}")
        
        # Generate new key if not found
        key = Fernet.generate_key()
        logger.warning(
            "Generated new encryption key. For production, set REPOSITORY_TOKEN_ENCRYPTION_KEY "
            f"environment variable to: {key.decode()}"
        )
        return key
    
    def store_token(
        self, 
        project: Project, 
        access_token: str, 
        expires_in_days: Optional[int] = None
    ) -> bool:
        """
        Encrypt and store PAT token for a project.
        
        Args:
            project: Project instance to store token for
            access_token: Plain text PAT token
            expires_in_days: Token expiration in days (default: 365)
            
        Returns:
            bool: True if successful
        """
        try:
            if not access_token or not access_token.strip():
                logger.error("Cannot store empty access token")
                return False
            
            # Encrypt the token
            encrypted_token = self.fernet.encrypt(access_token.encode()).decode()
            
            # Set expiration
            if expires_in_days:
                expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
            else:
                expires_at = datetime.now(timezone.utc) + timedelta(days=365)  # Default 1 year
            
            # Store in project
            project.encrypted_access_token = encrypted_token
            project.token_expires_at = expires_at
            project.token_last_used_at = datetime.now(timezone.utc)
            
            logger.info(f"📱 Stored encrypted token for project {project.name} (expires: {expires_at.strftime('%Y-%m-%d')})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store token for project {project.name}: {e}")
            return False
    
    def get_token(self, project: Project) -> Optional[str]:
        """
        Decrypt and return stored PAT token if valid.
        
        Args:
            project: Project instance to get token for
            
        Returns:
            Optional[str]: Decrypted token or None if invalid/expired
        """
        try:
            if not project.encrypted_access_token:
                logger.debug(f"No stored token for project {project.name}")
                return None
            
            # Check if token is expired
            if project.token_expires_at and project.token_expires_at < datetime.now(timezone.utc):
                logger.warning(f"🔑 Token expired for project {project.name}")
                self.invalidate_token(project)
                return None
            
            # Decrypt token
            decrypted_token = self.fernet.decrypt(project.encrypted_access_token.encode()).decode()
            
            # Update last used timestamp
            project.token_last_used_at = datetime.now(timezone.utc)
            
            logger.debug(f"✅ Retrieved valid token for project {project.name}")
            return decrypted_token
            
        except Exception as e:
            logger.error(f"Failed to decrypt token for project {project.name}: {e}")
            self.invalidate_token(project)
            return None
    
    def invalidate_token(self, project: Project) -> None:
        """
        Remove stored token from project.
        
        Args:
            project: Project instance to invalidate token for
        """
        project.encrypted_access_token = None
        project.token_expires_at = None
        logger.info(f"🗑️ Invalidated token for project {project.name}")
    
    def is_token_valid(self, project: Project) -> bool:
        """
        Check if project has a valid (non-expired) token.
        
        Args:
            project: Project instance to check
            
        Returns:
            bool: True if token exists and is not expired
        """
        return (
            project.encrypted_access_token is not None and
            (project.token_expires_at is None or 
             project.token_expires_at > datetime.now(timezone.utc))
        )
    
    def refresh_token_if_needed(self, project: Project, new_token: str) -> bool:
        """
        Update token if it's different from stored one.
        
        Args:
            project: Project instance
            new_token: New token to compare/store
            
        Returns:
            bool: True if token was updated
        """
        current_token = self.get_token(project)
        
        if current_token != new_token:
            logger.info(f"🔄 Updating token for project {project.name}")
            return self.store_token(project, new_token)
        
        # Token is same, just update last used
        project.token_last_used_at = datetime.now(timezone.utc)
        return True
    
    def cleanup_expired_tokens(self, db: Session) -> int:
        """
        Remove expired tokens from all projects.
        
        Args:
            db: Database session
            
        Returns:
            int: Number of tokens cleaned up
        """
        expired_projects = db.query(Project).filter(
            Project.token_expires_at < datetime.now(timezone.utc),
            Project.encrypted_access_token.isnot(None)
        ).all()
        
        count = 0
        for project in expired_projects:
            self.invalidate_token(project)
            count += 1
        
        if count > 0:
            db.commit()
            logger.info(f"🧹 Cleaned up {count} expired tokens")
        
        return count 