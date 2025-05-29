"""Add smart cache and token management fields to projects table

Revision ID: add_smart_cache_fields
Revises: 
Create Date: 2025-01-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = 'add_smart_cache_fields'
down_revision = None  # Update this to reference previous migration if any
branch_labels = None
depends_on = None


def upgrade():
    """Add smart cache and token management fields to projects table."""
    
    # Add cache management fields
    op.add_column('projects', sa.Column('cached_path', sa.String(500), nullable=True, comment='Local cache directory path'))
    op.add_column('projects', sa.Column('last_commit_hash', sa.String(40), nullable=True, comment='Last known git commit hash'))
    op.add_column('projects', sa.Column('cache_expires_at', sa.DateTime(timezone=True), nullable=True, comment='Cache expiration time'))
    op.add_column('projects', sa.Column('cache_size_mb', sa.Integer(), nullable=True, default=0, comment='Cache size in MB'))
    op.add_column('projects', sa.Column('auto_sync_enabled', sa.Boolean(), nullable=False, default=True, comment='Enable automatic git sync'))
    
    # Add token management fields
    op.add_column('projects', sa.Column('encrypted_access_token', sa.String(1000), nullable=True, comment='Encrypted PAT token'))
    op.add_column('projects', sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True, comment='Token expiration time'))
    op.add_column('projects', sa.Column('token_last_used_at', sa.DateTime(timezone=True), nullable=True, comment='Last time token was used'))
    
    # Create indexes for performance
    op.create_index('ix_projects_cache_expires_at', 'projects', ['cache_expires_at'])
    op.create_index('ix_projects_token_expires_at', 'projects', ['token_expires_at'])
    op.create_index('ix_projects_last_synced_at', 'projects', ['last_synced_at'])


def downgrade():
    """Remove smart cache and token management fields from projects table."""
    
    # Drop indexes
    op.drop_index('ix_projects_last_synced_at', table_name='projects')
    op.drop_index('ix_projects_token_expires_at', table_name='projects')
    op.drop_index('ix_projects_cache_expires_at', table_name='projects')
    
    # Drop token management fields
    op.drop_column('projects', 'token_last_used_at')
    op.drop_column('projects', 'token_expires_at')
    op.drop_column('projects', 'encrypted_access_token')
    
    # Drop cache management fields
    op.drop_column('projects', 'auto_sync_enabled')
    op.drop_column('projects', 'cache_size_mb')
    op.drop_column('projects', 'cache_expires_at')
    op.drop_column('projects', 'last_commit_hash')
    op.drop_column('projects', 'cached_path') 