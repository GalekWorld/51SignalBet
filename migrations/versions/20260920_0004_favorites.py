"""Create user favorites table."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0004"
down_revision = "20260920_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "favorites",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("favorite_type", sa.String(length=20), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_favorites_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_favorites"),
        sa.UniqueConstraint(
            "user_id", "favorite_type", "target_id", name="uq_favorites_user_type_target"
        ),
    )


def downgrade() -> None:
    op.drop_table("favorites")
