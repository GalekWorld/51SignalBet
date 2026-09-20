from uuid import uuid4

from app.db.base import Base
from app.db.models import Favorite
from app.domain.favorites import FavoriteType


def test_favorites_support_all_planned_target_types() -> None:
    assert {item.value for item in FavoriteType} == {"sport", "league", "team", "event", "player"}


def test_favorite_has_database_deduplication_constraint() -> None:
    table = Base.metadata.tables["favorites"]
    constraints = {constraint.name for constraint in table.constraints}

    assert "uq_favorites_user_type_target" in constraints
    assert Favorite.__table__.c.target_id is not None
    assert uuid4() != uuid4()
