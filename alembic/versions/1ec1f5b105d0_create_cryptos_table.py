# 1ec1f5b105d0_create_cryptos_table.py

"""create_cryptos_table

Revision ID: 1ec1f5b105d0
Revises: 123456789abc
Create Date: 2025-10-29 09:06:06.455328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ec1f5b105d0'
down_revision: Union[str, Sequence[str], None] = "123456789abc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        "cryptos",
        sa.Column("symbol", sa.String(length=20), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("current_price", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("cryptos")
