"""Add roles and audit log."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0010"
down_revision = "20260920_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("role", sa.String(length=20), nullable=False, server_default="user")
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=255), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_user_id"], ["users.id"], name="fk_audit_logs_actor_user_id_users"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_column("users", "role")
