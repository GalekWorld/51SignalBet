"""Create payment webhook history table."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0012"
down_revision = "20260920_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payment_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("external_event_id", sa.String(length=255), nullable=False),
        sa.Column("plan", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_payment_events_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_payment_events"),
        sa.UniqueConstraint(
            "provider", "external_event_id", name="uq_payment_events_provider_external"
        ),
    )


def downgrade() -> None:
    op.drop_table("payment_events")
