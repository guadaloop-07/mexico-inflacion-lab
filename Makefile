.PHONY: setup hooks check test db-up db-migrate test-db api setup-web web test-web build-web etl-bootstrap etl-refresh etl-reconcile

setup:
	uv sync --locked
	$(MAKE) hooks

hooks:
	uv run --locked pre-commit install --install-hooks --hook-type pre-commit

check:
	uv run --locked pre-commit run --all-files --hook-stage manual --show-diff-on-failure

test:
	uv run --locked pytest -m "not integration"

db-up:
	docker compose up --detach postgres

db-migrate:
	uv run --locked alembic upgrade head

test-db:
	uv run --locked pytest -m integration

api:
	uv run --locked uvicorn inflacion_lab.api.app:create_app --factory --reload

setup-web:
	npm ci --prefix web

web:
	npm run dev --prefix web

test-web:
	npm run test --prefix web

build-web:
	npm run build --prefix web

etl-bootstrap:
	uv run --locked inflacion-lab etl run --mode bootstrap

etl-refresh:
	uv run --locked inflacion-lab etl run --mode refresh

etl-reconcile:
	uv run --locked inflacion-lab etl run --mode reconcile
