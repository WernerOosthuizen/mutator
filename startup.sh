#!/bin/bash

./.venv/bin/alembic upgrade head
. ./.venv/bin/activate && gunicorn --threads=3 --workers=1 --log-file=- --access-logfile=- --bind ${HOST:-127.0.0.1}:${PORT:-8000} main:app
