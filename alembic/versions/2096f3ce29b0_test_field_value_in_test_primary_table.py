"""test field value in test_primary table

Revision ID: 2096f3ce29b0
Revises: b10d35c1bd9b
Create Date: 2024-10-19 14:59:18.027466

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2096f3ce29b0'
down_revision: Union[str, None] = 'b10d35c1bd9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tests_primary', sa.Column('test_value', sa.String(length=60), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tests_primary', 'test_value')
    # ### end Alembic commands ###