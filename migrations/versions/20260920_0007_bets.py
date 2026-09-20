"""Create tracked virtual bets table."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0007"
down_revision = "20260920_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bet_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("bookmaker_id", sa.Uuid(), nullable=True),
        sa.Column("market", sa.String(length=150), nullable=False),
        sa.Column("selection", sa.String(length=200), nullable=False),
        sa.Column("odds", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("stake", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("units", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("placed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["bookmaker_id"], ["bookmakers.id"], name="fk_bet_records_bookmaker_id_bookmakers"
        ),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], name="fk_bet_records_event_id_events"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_bet_records_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_bet_records"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_bet_records_user_idempotency"),
    )


def downgrade() -> None:
    op.drop_table("bet_records")
