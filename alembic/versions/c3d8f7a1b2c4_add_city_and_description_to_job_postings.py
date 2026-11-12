"""add_city_and_description_to_job_postings

Revision ID: c3d8f7a1b2c4
Revises: 8f1c4e2a3b5d
Create Date: 2026-11-12 10:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d8f7a1b2c4'
down_revision: Union[str, Sequence[str], None] = '8f1c4e2a3b5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add city and description optional columns to job_postings table."""
    with op.batch_alter_table('job_postings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('city', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('description', sa.String(length=500), nullable=True))
        batch_op.alter_column('title',
                              existing_type=sa.String(length=150),
                              type_=sa.String(length=120),
                              existing_nullable=False)


def downgrade() -> None:
    """Revert city and description columns from job_postings table."""
    with op.batch_alter_table('job_postings', schema=None) as batch_op:
        batch_op.drop_column('description')
        batch_op.drop_column('city')
        batch_op.alter_column('title',
                              existing_type=sa.String(length=120),
                              type_=sa.String(length=150),
                              existing_nullable=False)

