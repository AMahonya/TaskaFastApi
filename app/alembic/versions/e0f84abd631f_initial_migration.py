"""Initial migration

Revision ID: e0f84abd631f
Revises: 24bef182ce82
Create Date: 2024-12-16 17:16:32.926243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0f84abd631f'
down_revision: Union[str, None] = '24bef182ce82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String),
        sa.Column('email', sa.String),
        sa.Column('hashed_password', sa.String)
    )
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String),
        sa.Column('description', sa.String),
        sa.Column('completed', sa.Boolean),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    )


def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
