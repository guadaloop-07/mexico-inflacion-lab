.PHONY: setup hooks check test

setup:
	uv sync --locked
	$(MAKE) hooks

hooks:
	uv run --locked pre-commit install --install-hooks --hook-type pre-commit

check:
	uv run --locked pre-commit run --all-files --hook-stage manual --show-diff-on-failure

test:
	uv run --locked pytest -m "not integration"
