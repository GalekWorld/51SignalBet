"""Create Telegram users table."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0003"
down_revision = "20260920_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("telegram_user_id", name="uq_users_telegram_user_id"),
    )


def downgrade() -> None:
    op.drop_table("users")
