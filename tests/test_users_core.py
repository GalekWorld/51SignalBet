from app.db.base import Base
from app.db.models import User


def test_user_table_contains_telegram_identity_fields() -> None:
    table = Base.metadata.tables["users"]

    assert table.c.telegram_user_id is not None
    assert table.c.last_active_at.type.timezone is True
    assert User.__table__.primary_key is not None
