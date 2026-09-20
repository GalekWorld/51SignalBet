from uuid import uuid4

from app.services.event_detail import EventNotFound


def test_event_not_found_is_a_specific_domain_error() -> None:
    event_id = uuid4()

    assert issubclass(EventNotFound, LookupError)
    assert str(EventNotFound(f"event {event_id} was not found")).endswith("was not found")
