"""Create the initial sports domain tables."""

import sqlalchemy as sa
from alembic import op

revision = "20260920_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_sports"),
        sa.UniqueConstraint("code", name="uq_sports_code"),
    )
    op.create_table(
        "leagues",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sport_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["sport_id"], ["sports.id"], name="fk_leagues_sport_id_sports"),
        sa.PrimaryKeyConstraint("id", name="pk_leagues"),
        sa.UniqueConstraint("sport_id", "code", name="uq_leagues_sport_id_code"),
    )
    op.create_table(
        "teams",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sport_id", sa.Uuid(), nullable=False),
        sa.Column("league_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("normalized_name", sa.String(length=150), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["league_id"], ["leagues.id"], name="fk_teams_league_id_leagues"),
        sa.ForeignKeyConstraint(["sport_id"], ["sports.id"], name="fk_teams_sport_id_sports"),
        sa.PrimaryKeyConstraint("id", name="pk_teams"),
        sa.UniqueConstraint(
            "sport_id", "normalized_name", name="uq_teams_sport_id_normalized_name"
        ),
    )
    op.create_table(
        "players",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sport_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("normalized_name", sa.String(length=150), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["sport_id"], ["sports.id"], name="fk_players_sport_id_sports"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], name="fk_players_team_id_teams"),
        sa.PrimaryKeyConstraint("id", name="pk_players"),
        sa.UniqueConstraint(
            "sport_id", "normalized_name", name="uq_players_sport_id_normalized_name"
        ),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_event_id", sa.String(length=150), nullable=False),
        sa.Column("sport_id", sa.Uuid(), nullable=False),
        sa.Column("league_id", sa.Uuid(), nullable=True),
        sa.Column("home_team_id", sa.Uuid(), nullable=False),
        sa.Column("away_team_id", sa.Uuid(), nullable=False),
        sa.Column("season", sa.String(length=50), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("venue", sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(
            ["away_team_id"], ["teams.id"], name="fk_events_away_team_id_teams"
        ),
        sa.ForeignKeyConstraint(
            ["home_team_id"], ["teams.id"], name="fk_events_home_team_id_teams"
        ),
        sa.ForeignKeyConstraint(["league_id"], ["leagues.id"], name="fk_events_league_id_leagues"),
        sa.ForeignKeyConstraint(["sport_id"], ["sports.id"], name="fk_events_sport_id_sports"),
        sa.PrimaryKeyConstraint("id", name="pk_events"),
        sa.UniqueConstraint(
            "provider", "provider_event_id", name="uq_events_provider_provider_event_id"
        ),
    )
    op.create_index("ix_events_start_time", "events", ["start_time"])
    op.create_index("ix_events_status", "events", ["status"])


def downgrade() -> None:
    op.drop_index("ix_events_status", table_name="events")
    op.drop_index("ix_events_start_time", table_name="events")
    op.drop_table("events")
    op.drop_table("players")
    op.drop_table("teams")
    op.drop_table("leagues")
    op.drop_table("sports")
