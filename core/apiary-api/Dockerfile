FROM python:3.10-alpine as builder

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev cargo pkgconfig

RUN pip install poetry==1.7.0

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.10-alpine as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY apiary_api ./apiary_api

EXPOSE 8000

ENTRYPOINT ["uvicorn", "apiary_api.main:app", "--host", "0.0.0.0", "--port", "80"]
