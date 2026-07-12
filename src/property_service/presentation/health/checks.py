from __future__ import annotations

from sqlalchemy import select, text

from property_service.config import get_settings
from property_service.infrastructure.persistence.database import get_session_factory
from property_service.infrastructure.persistence.models import PropertyTypeLookupModel
from property_service.presentation.health.state import is_startup_complete


async def check_database() -> str:
    try:
        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:
        return f"error: {exc}"


async def check_redis() -> str:
    settings = get_settings()
    if settings.cache_backend == "memory":
        return "skipped"
    try:
        from property_service.infrastructure.cache.redis_client import get_redis_client

        redis = await get_redis_client()
        await redis.ping()
        return "ok"
    except Exception as exc:
        return f"error: {exc}"


async def check_rabbitmq() -> str:
    settings = get_settings()
    if settings.is_development:
        return "skipped"
    if not settings.rabbitmq_url:
        return "error: not configured"
    try:
        import aio_pika

        connection = await aio_pika.connect_robust(settings.rabbitmq_url, timeout=5)
        await connection.close()
        return "ok"
    except ImportError:
        return "skipped"
    except Exception as exc:
        return f"error: {exc}"


async def check_lookups_seeded() -> str:
    try:
        factory = get_session_factory()
        async with factory() as session:
            row = await session.execute(select(PropertyTypeLookupModel).limit(1))
            if row.scalar_one_or_none() is None:
                return "error: lookup tables empty"
        return "ok"
    except Exception as exc:
        return f"error: {exc}"


async def run_readiness_checks() -> tuple[dict[str, str], bool]:
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "rabbitmq": await check_rabbitmq(),
    }
    required = _required_readiness_checks()
    ready = all(checks[name] == "ok" for name in required)
    return checks, ready


def _required_readiness_checks() -> tuple[str, ...]:
    settings = get_settings()
    if settings.is_development:
        return ("database",)
    required: list[str] = ["database"]
    if settings.cache_backend == "redis":
        required.append("redis")
    required.append("rabbitmq")
    return tuple(required)


async def run_startup_checks() -> tuple[dict[str, str], bool]:
    checks = {
        "startup": "ok" if is_startup_complete() else "pending",
        "lookups": await check_lookups_seeded(),
    }
    started = checks["startup"] == "ok" and checks["lookups"] == "ok"
    return checks, started
