"""Create virtual bankroll ledger tables."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0006"
down_revision = "20260920_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bankrolls",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_bankrolls_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_bankrolls"),
        sa.UniqueConstraint("user_id", name="uq_bankrolls_user_id"),
    )
    op.create_table(
        "bankroll_transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("bankroll_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_type", sa.String(length=30), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("reference_id", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["bankroll_id"], ["bankrolls.id"], name="fk_bankroll_transactions_bankroll_id_bankrolls"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_bankroll_transactions"),
        sa.UniqueConstraint(
            "bankroll_id", "idempotency_key", name="uq_bankroll_transactions_idempotency"
        ),
    )


def downgrade() -> None:
    op.drop_table("bankroll_transactions")
    op.drop_table("bankrolls")
