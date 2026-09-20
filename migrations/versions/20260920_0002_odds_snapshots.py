"""Create bookmaker and append-only odds snapshot tables."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0002"
down_revision = "20260920_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bookmakers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_bookmakers"),
        sa.UniqueConstraint("code", name="uq_bookmakers_code"),
    )
    op.create_table(
        "odds_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("bookmaker_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_line_id", sa.String(length=150), nullable=False),
        sa.Column("market_key", sa.String(length=150), nullable=False),
        sa.Column("selection", sa.String(length=200), nullable=True),
        sa.Column("line", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("odds", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("provider_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["bookmaker_id"], ["bookmakers.id"], name="fk_odds_snapshots_bookmaker_id_bookmakers"
        ),
        sa.ForeignKeyConstraint(
            ["event_id"], ["events.id"], name="fk_odds_snapshots_event_id_events"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_odds_snapshots"),
        sa.UniqueConstraint(
            "provider", "provider_line_id", "provider_ts", name="uq_odds_snapshots_provider_line_ts"
        ),
    )
    op.create_index(
        "ix_odds_snapshots_event_market_provider_ts",
        "odds_snapshots",
        ["event_id", "market_key", "provider_ts"],
    )
    op.create_index(
        "ix_odds_snapshots_bookmaker_provider_ts",
        "odds_snapshots",
        ["bookmaker_id", "provider_ts"],
    )


def downgrade() -> None:
    op.drop_index("ix_odds_snapshots_bookmaker_provider_ts", table_name="odds_snapshots")
    op.drop_index("ix_odds_snapshots_event_market_provider_ts", table_name="odds_snapshots")
    op.drop_table("odds_snapshots")
    op.drop_table("bookmakers")
