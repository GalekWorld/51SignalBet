# Betting Platform

Plataforma modular de análisis de apuestas deportivas y seguimiento virtual,
preparada para integrarse con Telegram. El sistema no ejecuta apuestas ni se
conecta a cuentas personales de bookmakers.

## Estado

Fase 51 — Optimization based on real usage.

El sistema ya dispone de la base completa del roadmap: motor de cuotas y valor,
Telegram, bankroll, tracking, settlement, estadísticas, investigación,
backtesting, modelos versionados, explainability y salvaguardas de plataforma.

## Desarrollo local

Requiere Python 3.12+ y Docker. Copia `.env.example` a `.env` y arranca:

```text
docker compose up --build
```

La API queda disponible en `http://localhost:8000/health`.

Para trabajar con el entorno Python:

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e . --group dev
pytest
ruff check .
mypy app
```

## Principios

- Arquitectura modular dentro de un único proyecto.
- PostgreSQL será la fuente persistente de verdad; Redis será temporal.
- Las integraciones externas quedarán detrás de adapters propios.
- Las fechas internas serán UTC y los importes/cuotas usarán `Decimal` cuando se implementen.
- Las funcionalidades se incorporan por fase, con tests y migraciones cuando correspondan.
