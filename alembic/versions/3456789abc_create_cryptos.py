# 3456789abc_create_cryptos.py
"""create cryptos table

Revision ID: 3456789abc
Revises: 123456789abc
Create Date: 2025-10-18 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# identifiers
revision = "3456789abc"
down_revision = "123456789abc"
branch_labels = None
depends_on = None


def upgrade():
    # таблица для хранения одной криптовалюты в строке
    op.create_table(
        "cryptos",
        sa.Column("id", sa.Integer, primary_key=True),
        # символ (BTC, ETH и т.д.)
        sa.Column("symbol", sa.String(length=20), nullable=False),
        # читаемое имя
        sa.Column("name", sa.String(length=255), nullable=False),
        # цена — Decimal; precision/scale можно подправить под ваши нужды
        sa.Column("current_price", sa.Numeric(precision=20, scale=8), nullable=False),
        # время последнего обновления в UTC (timezone-aware)
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=False),
        # время создания записи
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.UniqueConstraint("symbol", name="uq_cryptos_symbol"),
    )

    # индекс по symbol для быстрых выборок
    op.create_index("ix_cryptos_symbol", "cryptos", ["symbol"])


def downgrade():
    op.drop_index("ix_cryptos_symbol", table_name="cryptos")
    op.drop_table("cryptos")
