"""create_job_postings_and_applications_tables

Revision ID: 8f1c4e2a3b5d
Revises: 4b4900ce1c26
Create Date: 2026-10-21 09:38:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f1c4e2a3b5d'
down_revision: Union[str, Sequence[str], None] = '4b4900ce1c26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to include job_postings and applications tables."""
    # 1. Create 'job_postings' table (One User to Many Postings)
    op.create_table(
        'job_postings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('company', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_postings_id'), 'job_postings', ['id'], unique=False)
    op.create_index(op.f('ix_job_postings_user_id'), 'job_postings', ['user_id'], unique=False)

    # 2. Create 'applications' join table (Many Users to Many Postings)
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_posting_id', sa.Integer(), sa.ForeignKey('job_postings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='applied', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'job_posting_id', name='uq_user_job_application')
    )
    op.create_index(op.f('ix_applications_id'), 'applications', ['id'], unique=False)
    op.create_index(op.f('ix_applications_user_id'), 'applications', ['user_id'], unique=False)
    op.create_index(op.f('ix_applications_job_posting_id'), 'applications', ['job_posting_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema: drop applications first, then job_postings."""
    op.drop_index(op.f('ix_applications_job_posting_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_user_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_id'), table_name='applications')
    op.drop_table('applications')

    op.drop_index(op.f('ix_job_postings_user_id'), table_name='job_postings')
    op.drop_index(op.f('ix_job_postings_id'), table_name='job_postings')
    op.drop_table('job_postings')
