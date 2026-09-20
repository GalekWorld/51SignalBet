# Modelo de datos actual

La Fase 5 añade `bookmakers` y `odds_snapshots`.

`OddsSnapshot` conserva el evento, bookmaker interno, mercado, selección, línea,
cuota, proveedor, identificador de línea, timestamp del proveedor y timestamp de
recepción. Las filas históricas no se actualizan durante la ingesta; una nueva
observación crea una nueva fila.

Los importes de cuota y línea usan `Numeric(12, 4)` en PostgreSQL y `Decimal` en
los modelos normalizados. Los timestamps son timezone-aware. La unicidad de
`provider + provider_line_id + provider_ts` evita duplicar exactamente la misma
observación sin borrar cambios reales en el tiempo.
