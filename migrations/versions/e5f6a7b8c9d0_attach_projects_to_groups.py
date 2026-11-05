"""Attach projects to a project group

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-11-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project', sa.Column('group_id', sa.Integer(), nullable=True))

    connection = op.get_bind()
    uncategorized_id = connection.execute(
        sa.text("SELECT id FROM project_group WHERE slug = 'uncategorized'")
    ).scalar()

    if uncategorized_id is None:
        connection.execute(
            sa.text(
                "INSERT INTO project_group (name, slug) "
                "VALUES ('Uncategorized', 'uncategorized')"
            )
        )
        uncategorized_id = connection.execute(
            sa.text("SELECT id FROM project_group WHERE slug = 'uncategorized'")
        ).scalar()

    connection.execute(
        sa.text("UPDATE project SET group_id = :group_id"),
        {"group_id": uncategorized_id},
    )

    op.alter_column(
        'project',
        'group_id',
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        'fk_project_group_id',
        'project',
        'project_group',
        ['group_id'],
        ['id'],
    )


def downgrade():
    op.drop_constraint('fk_project_group_id', 'project', type_='foreignkey')
    op.drop_column('project', 'group_id')
