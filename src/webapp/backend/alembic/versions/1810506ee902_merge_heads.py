"""merge_heads

Revision ID: 1810506ee902
Revises: 32573108a3e7, add_smart_cache_fields
Create Date: 2025-05-29 12:39:47.531462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1810506ee902'
down_revision: Union[str, None] = ('32573108a3e7', 'add_smart_cache_fields')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
