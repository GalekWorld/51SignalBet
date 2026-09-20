"""Create settlement history table."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0008"
down_revision = "20260920_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "settlement_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("bet_id", sa.Uuid(), nullable=False),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payout_amount", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.ForeignKeyConstraint(
            ["bet_id"], ["bet_records.id"], name="fk_settlement_events_bet_id_bet_records"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_settlement_events"),
        sa.UniqueConstraint("bet_id", name="uq_settlement_events_bet_id"),
    )


def downgrade() -> None:
    op.drop_table("settlement_events")
