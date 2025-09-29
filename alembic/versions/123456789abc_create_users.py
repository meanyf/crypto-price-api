# 123456789abc_create_users.py

"""create users table

Revision ID: 123456789abc
Revises:
Create Date: 2025-09-29 14:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# идентификаторы ревизии
revision = "123456789abc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("username", sa.String, nullable=False, unique=True, index=True),
        sa.Column("password", sa.String, nullable=False),
    )


def downgrade():
    op.drop_table("users")
