FROM python:3.11-slim-bullseye as base

WORKDIR /app

FROM base as builder
ENV POETRY_VERSION=1.4.0 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

COPY ./poetry.lock ./pyproject.toml /app/
RUN pip install "poetry==$POETRY_VERSION" \
    && poetry install --no-dev

FROM base as final

COPY --from=builder /app/.venv /app/.venv/
COPY ./alembic /app/alembic/
COPY ./alembic.ini /app/
COPY ./src /app/src/
COPY ./data/database /app/data/database
COPY ./main.py /app/
COPY ./startup.sh /app/
CMD /app/startup.sh
