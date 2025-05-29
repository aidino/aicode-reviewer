"""Add smart cache and token management fields to projects table

Revision ID: add_smart_cache_fields
Revises: 32573108a3e7
Create Date: 2025-01-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = 'add_smart_cache_fields'
down_revision = '32573108a3e7'  # Depends on auth tables migration
branch_labels = None
depends_on = None


def upgrade():
    """Create projects table with smart cache and token management fields."""
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('language', sa.String(length=50), nullable=True),
        sa.Column('default_branch', sa.String(length=100), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=False, default=False),
        sa.Column('stars', sa.Integer(), nullable=True, default=0),
        sa.Column('forks', sa.Integer(), nullable=True, default=0),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        
        # Smart cache management fields
        sa.Column('cached_path', sa.String(500), nullable=True, comment='Local cache directory path'),
        sa.Column('last_commit_hash', sa.String(40), nullable=True, comment='Last known git commit hash'),
        sa.Column('cache_expires_at', sa.DateTime(timezone=True), nullable=True, comment='Cache expiration time'),
        sa.Column('cache_size_mb', sa.Integer(), nullable=True, default=0, comment='Cache size in MB'),
        sa.Column('auto_sync_enabled', sa.Boolean(), nullable=False, default=True, comment='Enable automatic git sync'),
        
        # Token management fields
        sa.Column('encrypted_access_token', sa.String(1000), nullable=True, comment='Encrypted PAT token'),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True, comment='Token expiration time'),
        sa.Column('token_last_used_at', sa.DateTime(timezone=True), nullable=True, comment='Last time token was used'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('url')
    )
    
    # Create indexes for performance
    op.create_index('ix_projects_id', 'projects', ['id'])
    op.create_index('ix_projects_owner_id', 'projects', ['owner_id'])
    op.create_index('ix_projects_cache_expires_at', 'projects', ['cache_expires_at'])
    op.create_index('ix_projects_token_expires_at', 'projects', ['token_expires_at'])
    op.create_index('ix_projects_last_synced_at', 'projects', ['last_synced_at'])


def downgrade():
    """Drop projects table."""
    
    # Drop indexes
    op.drop_index('ix_projects_last_synced_at', table_name='projects')
    op.drop_index('ix_projects_token_expires_at', table_name='projects')
    op.drop_index('ix_projects_cache_expires_at', table_name='projects')
    op.drop_index('ix_projects_owner_id', table_name='projects')
    op.drop_index('ix_projects_id', table_name='projects')
    
    # Drop table
    op.drop_table('projects') 