from app.core.text import normalize_name
from app.services.search import SearchPage


def test_search_normalizes_accents_before_querying() -> None:
    assert normalize_name("Real  Madrid") == "real madrid"
    assert normalize_name("Atlético") == "atletico"


def test_empty_search_page_has_no_continuation() -> None:
    page = SearchPage(items=[], next_offset=None)

    assert page.items == []
    assert page.next_offset is None
