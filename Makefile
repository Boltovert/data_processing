.PHONY: lint
lint:
	poetry run ruff check
	poetry run mypy ./src ./bin
