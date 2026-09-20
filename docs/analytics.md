# Motor matemático

`app.analytics.odds_math` es independiente de Telegram, FastAPI, SQLAlchemy y
los providers.

El motor diferencia explícitamente entre probabilidad implícita bruta,
probabilidad fair de mercado y probabilidad del modelo. La eliminación de margen
actual usa el método proporcional sobre el mercado completo. `edge` se expresa
como diferencia de probabilidades; `expected_value` como beneficio esperado por
unidad apostada.

Todas las operaciones usan `Decimal`; no se utiliza `float` para cuotas ni
probabilidades.
