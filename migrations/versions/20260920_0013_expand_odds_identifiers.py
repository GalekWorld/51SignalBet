"""Allow provider odds identifiers used by real prop markets."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0013"
down_revision = "20260920_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "odds_snapshots",
        "provider_line_id",
        existing_type=sa.String(length=150),
        type_=sa.String(length=500),
        existing_nullable=False,
    )
    op.alter_column(
        "odds_snapshots",
        "market_key",
        existing_type=sa.String(length=150),
        type_=sa.String(length=500),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "odds_snapshots",
        "market_key",
        existing_type=sa.String(length=500),
        type_=sa.String(length=150),
        existing_nullable=False,
    )
    op.alter_column(
        "odds_snapshots",
        "provider_line_id",
        existing_type=sa.String(length=500),
        type_=sa.String(length=150),
        existing_nullable=False,
    )
