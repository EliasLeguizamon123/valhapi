"""Remove test_value field from TestPrimary

Revision ID: bb9a17f74453
Revises: 6e6d2a48cc95
Create Date: 2024-10-19 15:04:17.703791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb9a17f74453'
down_revision: Union[str, None] = '6e6d2a48cc95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tests_primary', 'test_value')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tests_primary', sa.Column('test_value', sa.VARCHAR(length=60), nullable=True))
    # ### end Alembic commands ###
