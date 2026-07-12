#!/bin/bash
# docker/entrypoint.sh
set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    python -m alembic upgrade head
fi

if [ "$SEED_LOOKUPS" = "true" ]; then
    echo "Seeding lookup tables..."
    PYTHONPATH="/app/src:/app" python -m scripts.seed_property_types
fi

exec "$@"
