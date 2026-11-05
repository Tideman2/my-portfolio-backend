"""Align project columns with the model

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-11-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'project',
        'title',
        existing_type=sa.String(length=100),
        type_=sa.String(length=150),
        existing_nullable=False,
    )
    op.alter_column(
        'project',
        'image',
        existing_type=sa.String(length=100),
        type_=sa.String(length=500),
        existing_nullable=True,
    )
    op.alter_column(
        'project',
        'stack',
        existing_type=sa.String(length=200),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        'project',
        'goal',
        existing_type=sa.String(length=300),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        'project',
        'github_url',
        existing_type=sa.String(length=200),
        type_=sa.String(length=500),
        existing_nullable=True,
    )
    op.alter_column(
        'project',
        'demo_url',
        existing_type=sa.String(length=200),
        type_=sa.String(length=500),
        existing_nullable=True,
    )


def downgrade():
    op.alter_column(
        'project',
        'demo_url',
        existing_type=sa.String(length=500),
        type_=sa.String(length=200),
        existing_nullable=True,
    )
    op.alter_column(
        'project',
        'github_url',
        existing_type=sa.String(length=500),
        type_=sa.String(length=200),
        existing_nullable=True,
    )
    op.alter_column(
        'project',
        'goal',
        existing_type=sa.Text(),
        type_=sa.String(length=300),
        existing_nullable=True,
    )
    op.alter_column(
        'project',
        'stack',
        existing_type=sa.String(length=255),
        type_=sa.String(length=200),
        existing_nullable=True,
    )
    op.alter_column(
        'project',
        'image',
        existing_type=sa.String(length=500),
        type_=sa.String(length=100),
        existing_nullable=True,
    )
    op.alter_column(
        'project',
        'title',
        existing_type=sa.String(length=150),
        type_=sa.String(length=100),
        existing_nullable=False,
    )
