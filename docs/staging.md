# Staging

## Requisitos

- Python 3.12+ para ejecución local.
- Docker y Docker Compose.
- PostgreSQL 16 y Redis 7 mediante Compose.
- `ODDS_API_KEY` para sincronización real.
- `TELEGRAM_BOT_TOKEN` para arrancar el bot.

Para staging, copia `.env.staging.example` a `.env` y sustituye todos los
placeholders fuera del repositorio. Nunca guardes ese fichero con secretos en Git.

## Arranque

```text
Copy-Item .env.staging.example .env
# completar secretos solo en el entorno local/staging
docker compose up --build
```

La validación de build y arranque debe realizarse con Docker Desktop activo. La
suite CI usa una base independiente llamada `betting_test`; staging usa
`betting_staging`.

Compose ejecuta el servicio `migrate` antes de API, bot y worker. La API expone
`/health/live`, `/health/ready` y `/health/provider`.

## Checks

```text
pytest -q
ruff check .
ruff format --check .
mypy app/domain app/services app/providers app/analytics app/ml app/jobs
python scripts/provider_smoke.py
```

Con el stack levantado, comprobar además:

```text
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/health/live
Invoke-RestMethod http://localhost:8000/health/ready
Invoke-WebRequest http://localhost:8000/openapi.json
docker compose ps
docker compose logs --tail=100 api worker bot migrate
```

El smoke del provider requiere una API key real y no forma parte del CI estándar.

El smoke de Telegram requiere `TELEGRAM_BOT_TOKEN` y se valida manualmente con
`/start` y el flujo principal. No se debe ejecutar una campaña masiva en staging.

## Rollback básico

Detener servicios con `docker compose down`, conservar el volumen PostgreSQL y
aplicar una migración correctiva hacia delante. No usar reset destructivo en datos
de staging; restaurar un backup verificado si una reversión de datos es necesaria.

## Parada limpia

```text
docker compose down
```

La CI remota está configurada para Python 3.12, PostgreSQL, Redis, Ruff, formato,
mypy, Alembic y pytest; debe marcarse `CI CONFIGURED — NOT REMOTELY VERIFIED`
hasta observar una ejecución real en GitHub Actions.
