# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /build

RUN python -m venv /build/.venv
ENV PATH="/build/.venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e .

# Stage 2: Runtime
FROM python:3.12-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/src /app/src
COPY alembic.ini /app/
COPY migrations /app/migrations
COPY scripts /app/scripts
COPY docker/entrypoint.sh /app/entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN chmod +x /app/entrypoint.sh
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "property_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
