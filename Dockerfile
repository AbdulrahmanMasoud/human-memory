# ============================================================
# Stage 0: Frontend — build Vue app
# ============================================================
FROM node:22-alpine AS frontend

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npx vite build

# ============================================================
# Stage 1: Builder — install Python dependencies
# ============================================================
FROM python:3.13-alpine AS builder

RUN apk add --no-cache gcc g++ musl-dev libffi-dev openssl-dev postgresql-dev git

COPY pyproject.toml /app/
WORKDIR /app

RUN python -m venv /app/.venv \
    && . /app/.venv/bin/activate \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

COPY src/ /app/src/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/

# ============================================================
# Stage 2: Runtime — pure Alpine
# ============================================================
FROM python:3.13-alpine AS runtime

RUN apk add --no-cache libstdc++ libffi openssl libpq

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/alembic.ini /app/
COPY --from=frontend /frontend/dist /app/frontend/dist

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "memory_system.main:app", "--host", "0.0.0.0", "--port", "8000"]
