"""create all tables

Revision ID: 91fd3387cc2d
Revises: 
Create Date: 2024-01-23 18:19:40.276961

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91fd3387cc2d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('name', 'id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user_table',
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('surname', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('birthday', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('id')
    )
    op.create_table('refresh_session',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('refresh_token', sa.UUID(), nullable=True),
    sa.Column('finger_print', sa.String(), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user_table.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('user_role',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role_name', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['role_name'], ['role.name'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user_table.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', 'user_id', 'role_name'),
    sa.UniqueConstraint('id')
    )
    op.create_table('login_history',
    sa.Column('agent_id', sa.UUID(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('action', sa.String(length=10), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['refresh_session.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('login_history')
    op.drop_table('user_role')
    op.drop_table('refresh_session')
    op.drop_table('user_table')
    op.drop_table('role')
    # ### end Alembic commands ###