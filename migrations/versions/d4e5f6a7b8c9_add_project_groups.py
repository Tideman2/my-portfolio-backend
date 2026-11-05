"""Add project groups

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-11-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'project_group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug'),
    )

    group_table = sa.table(
        'project_group',
        sa.column('name', sa.String),
        sa.column('slug', sa.String),
    )
    op.bulk_insert(
        group_table,
        [{'name': 'Uncategorized', 'slug': 'uncategorized'}],
    )


def downgrade():
    op.drop_table('project_group')
