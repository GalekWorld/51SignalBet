# Bet tracking

`BetRecord` registra picks virtuales con evento, mercado, selección, bookmaker,
cuota, stake, unidades, timestamp, fuente y estado. La operación es idempotente
por usuario y `idempotency_key`.

Esta fase no liquida resultados ni modifica el bankroll. Settlement y sus
transacciones ledger corresponden a la fase siguiente.
