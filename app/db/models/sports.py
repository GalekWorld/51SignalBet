"""Persistence models for the sports domain."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedModel
from app.domain.sports import EventStatus, validate_event_participants


class Sport(TimestampedModel):
    __tablename__ = "sports"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    leagues: Mapped[list["League"]] = relationship(back_populates="sport")
    teams: Mapped[list["Team"]] = relationship(back_populates="sport")
    events: Mapped[list["Event"]] = relationship(back_populates="sport")


class League(TimestampedModel):
    __tablename__ = "leagues"
    __table_args__ = (UniqueConstraint("sport_id", "code", name="uq_leagues_sport_id_code"),)

    sport_id: Mapped[UUID] = mapped_column(ForeignKey("sports.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sport: Mapped[Sport] = relationship(back_populates="leagues")
    teams: Mapped[list["Team"]] = relationship(back_populates="league")
    events: Mapped[list["Event"]] = relationship(back_populates="league")


class Team(TimestampedModel):
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint("sport_id", "normalized_name", name="uq_teams_sport_id_normalized_name"),
    )

    sport_id: Mapped[UUID] = mapped_column(ForeignKey("sports.id"), nullable=False)
    league_id: Mapped[UUID | None] = mapped_column(ForeignKey("leagues.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(150), nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sport: Mapped[Sport] = relationship(back_populates="teams")
    league: Mapped[League | None] = relationship(back_populates="teams")
    home_events: Mapped[list["Event"]] = relationship(
        back_populates="home_team", foreign_keys="Event.home_team_id"
    )
    away_events: Mapped[list["Event"]] = relationship(
        back_populates="away_team", foreign_keys="Event.away_team_id"
    )


class Player(TimestampedModel):
    __tablename__ = "players"
    __table_args__ = (
        UniqueConstraint("sport_id", "normalized_name", name="uq_players_sport_id_normalized_name"),
    )

    sport_id: Mapped[UUID] = mapped_column(ForeignKey("sports.id"), nullable=False)
    team_id: Mapped[UUID | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sport: Mapped[Sport] = relationship()
    team: Mapped[Team | None] = relationship()


class Event(TimestampedModel):
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint(
            "provider", "provider_event_id", name="uq_events_provider_provider_event_id"
        ),
        Index("ix_events_start_time", "start_time"),
        Index("ix_events_status", "status"),
    )

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_event_id: Mapped[str] = mapped_column(String(150), nullable=False)
    sport_id: Mapped[UUID] = mapped_column(ForeignKey("sports.id"), nullable=False)
    league_id: Mapped[UUID | None] = mapped_column(ForeignKey("leagues.id"), nullable=True)
    home_team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id"), nullable=False)
    season: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[EventStatus] = mapped_column(
        String(20), default=EventStatus.SCHEDULED, nullable=False
    )
    home_score: Mapped[int | None] = mapped_column(nullable=True)
    away_score: Mapped[int | None] = mapped_column(nullable=True)
    venue: Mapped[str | None] = mapped_column(String(200), nullable=True)

    sport: Mapped[Sport] = relationship(back_populates="events")
    league: Mapped[League | None] = relationship(back_populates="events")
    home_team: Mapped[Team] = relationship(
        back_populates="home_events", foreign_keys=[home_team_id]
    )
    away_team: Mapped[Team] = relationship(
        back_populates="away_events", foreign_keys=[away_team_id]
    )

    def __init__(self, **kwargs: object) -> None:
        validate_event_participants(kwargs["home_team_id"], kwargs["away_team_id"])
        super().__init__(**kwargs)
