POETRY_RUN = poetry run

flask:
	$(POETRY_RUN) gunicorn -w 1 -b 0.0.0.0:8002 flask_tcc.main:app