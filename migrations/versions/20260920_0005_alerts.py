"""Create alert rules and trigger history tables."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0005"
down_revision = "20260920_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("metric", sa.String(length=30), nullable=False),
        sa.Column("operator", sa.String(length=10), nullable=False),
        sa.Column("threshold", sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column("filters", sa.JSON(), nullable=False),
        sa.Column("cooldown_seconds", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_alert_rules_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_alert_rules"),
    )
    op.create_table(
        "alert_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rule_id", sa.Uuid(), nullable=False),
        sa.Column("dedup_key", sa.String(length=255), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["rule_id"], ["alert_rules.id"], name="fk_alert_events_rule_id_alert_rules"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_alert_events"),
        sa.UniqueConstraint("rule_id", "dedup_key", name="uq_alert_events_rule_dedup_key"),
    )


def downgrade() -> None:
    op.drop_table("alert_events")
    op.drop_table("alert_rules")
