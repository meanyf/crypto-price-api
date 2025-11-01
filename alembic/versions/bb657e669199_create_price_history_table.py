# bb657e669199_create_price_history_table.py

"""create_price_history_table

Revision ID: bb657e669199
Revises: 1ec1f5b105d0
Create Date: 2025-10-31 08:36:33.055310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb657e669199'
down_revision: Union[str, Sequence[str], None] = '1ec1f5b105d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "price_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "symbol",
            sa.String(length=20),
            sa.ForeignKey("cryptos.symbol", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("price", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_price_history_symbol_timestamp", "price_history", ["symbol", "timestamp"]
    )


def downgrade():
    op.drop_index("ix_price_history_symbol_timestamp", table_name="price_history")
    op.drop_table("price_history")
