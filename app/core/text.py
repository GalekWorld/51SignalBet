"""Text normalization helpers used when mapping external names."""

import unicodedata


def normalize_name(value: str) -> str:
    """Normalize case and accents while preserving word boundaries."""

    decomposed = unicodedata.normalize("NFKD", value)
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(without_marks.casefold().split())
