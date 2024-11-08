POETRY_RUN = poetry run

flask:
	$(POETRY_RUN) gunicorn -w 1 -b 0.0.0.0:8002 flask_tcc.main:app

#* Formatters
.PHONY: format
format:
	@poetry run ruff format .

#* Linting
.PHONY: lint
lint:
	@poetry run ruff check .
	@poetry run ruff format --check .