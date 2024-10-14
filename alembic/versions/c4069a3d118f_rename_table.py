"""Rename table

Revision ID: c4069a3d118f
Revises: ab4781a73c31
Create Date: 2024-10-13 23:46:04.825214

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c4069a3d118f'
down_revision: Union[str, None] = 'ab4781a73c31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('messages',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('chat_id', sa.UUID(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('line_type', sa.Enum('USER', 'SYSTEM', name='messagetype'), nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('chat_lines')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_lines',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('chat_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('line_type', postgresql.ENUM('USER', 'SYSTEM', name='chatlinetype'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], name='chat_lines_chat_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='chat_lines_pkey')
    )
    op.drop_table('messages')
    # ### end Alembic commands ###
