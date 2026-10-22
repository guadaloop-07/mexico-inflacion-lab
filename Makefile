.PHONY: setup hooks check test db-up db-migrate test-db

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
