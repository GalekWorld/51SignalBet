from datetime import UTC, datetime

from app.services.today_events import timezone_or_utc, today_window_utc


def test_today_window_converts_local_calendar_day_to_utc() -> None:
    start, end = today_window_utc(
        "Europe/Madrid",
        now=datetime(2026, 9, 20, 12, tzinfo=UTC),
    )

    assert start == datetime(2026, 9, 19, 22, tzinfo=UTC)
    assert end == datetime(2026, 9, 20, 22, tzinfo=UTC)


def test_invalid_user_timezone_falls_back_to_utc() -> None:
    assert timezone_or_utc("not/a-timezone").key == "UTC"
