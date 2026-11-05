"""Add profile and socials

Revision ID: b7f1c2d4e5a6
Revises: 04b1db3c6005
Create Date: 2026-11-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7f1c2d4e5a6'
down_revision = '04b1db3c6005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'profile',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'social',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('platform_name', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('social')
    op.drop_table('profile')
