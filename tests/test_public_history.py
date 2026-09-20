from app.db.base import Base
from app.db.models import PublishedPick


def test_published_pick_stores_an_immutable_publication_snapshot() -> None:
    table = Base.metadata.tables["published_picks"]
    constraints = {constraint.name for constraint in table.constraints}

    assert "uq_published_picks_publication_key" in constraints
    assert table.c.published_at.type.timezone is True
    assert PublishedPick.__table__.c.odds.type.scale == 4
