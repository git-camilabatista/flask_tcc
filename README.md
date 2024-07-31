How to run?

```sh
poetry run gunicorn -w 1 -b 0.0.0.0:8002 flask_tcc.main:app
```

or using Makefile

```sh
make flask
```