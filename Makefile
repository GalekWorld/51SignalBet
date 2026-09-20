.PHONY: up down test lint format typecheck migrate smoke-provider logs

up:
	docker compose up --build

down:
	docker compose down

test:
	pytest -q

lint:
	ruff check .

format:
	ruff format --check .

typecheck:
	mypy app/domain app/services app/providers app/analytics app/ml app/jobs

migrate:
	docker compose run --rm migrate

smoke-provider:
	python scripts/provider_smoke.py

logs:
	docker compose logs -f
