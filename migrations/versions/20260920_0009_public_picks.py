"""Create immutable published picks table."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0009"
down_revision = "20260920_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "published_picks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("bookmaker_id", sa.Uuid(), nullable=False),
        sa.Column("market", sa.String(length=150), nullable=False),
        sa.Column("selection", sa.String(length=200), nullable=False),
        sa.Column("odds", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("fair_probability", sa.Numeric(precision=12, scale=8), nullable=False),
        sa.Column("model_probability", sa.Numeric(precision=12, scale=8), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("strategy_version", sa.String(length=100), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("publication_key", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["bookmaker_id"], ["bookmakers.id"], name="fk_published_picks_bookmaker_id_bookmakers"
        ),
        sa.ForeignKeyConstraint(
            ["event_id"], ["events.id"], name="fk_published_picks_event_id_events"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_published_picks"),
        sa.UniqueConstraint("publication_key", name="uq_published_picks_publication_key"),
    )


def downgrade() -> None:
    op.drop_table("published_picks")
