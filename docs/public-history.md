# Historial público

`PublishedPick` guarda una fotografía completa en el momento de publicación:
evento, mercado, selección, bookmaker, cuota, fair probability, eventual model
probability, estrategia y timestamps.

El historial no recalcula cuotas retrospectivamente. `publication_key` hace
idempotente la publicación y evita duplicar el mismo pick público.
