# Comparador de bookmakers

`OddsComparisonService` recibe cuotas ya normalizadas y no conoce Telegram,
FastAPI ni SQLAlchemy. Para cada selección calcula mejor y peor cuota, media,
mediana, spread y número de bookmakers.

Cuando se proporciona una fair odd, `difference_vs_fair` se calcula como
`best_odds / fair_odds - 1`. La fair odd debe proceder de una fuente de
probabilidad fair explícita; el comparador no la inventa a partir de una sola
cuota.
