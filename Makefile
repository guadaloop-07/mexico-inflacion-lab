.PHONY: setup hooks check

setup:
	uv sync --locked
	$(MAKE) hooks

hooks:
	uv run --locked pre-commit install --install-hooks --hook-type pre-commit

check:
	uv run --locked pre-commit run --all-files --hook-stage manual --show-diff-on-failure
