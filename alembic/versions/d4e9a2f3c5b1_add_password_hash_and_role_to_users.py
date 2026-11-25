"""add_password_hash_and_role_to_users

Revision ID: d4e9a2f3c5b1
Revises: c3d8f7a1b2c4
Create Date: 2026-11-25 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e9a2f3c5b1'
down_revision: Union[str, Sequence[str], None] = 'c3d8f7a1b2c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password_hash and role columns to users table for authentication & authorization."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=255), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('role', sa.String(length=30), nullable=False, server_default='graduate'))


def downgrade() -> None:
    """Remove password_hash and role columns from users table."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('role')
        batch_op.drop_column('password_hash')
