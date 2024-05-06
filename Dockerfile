FROM python:3.12-slim as builder

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
    DAGSHUB_TOKEN=2ea1892ddf473f9f3b467201b8497b5e7c6eade0

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --without dev --without win-dev --no-root

FROM python:3.12-slim as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . ./app

WORKDIR /app

CMD ["uvicorn", "src.serve.main:app", "--host", "0.0.0.0", "--port", "8000"]