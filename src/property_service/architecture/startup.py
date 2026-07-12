from __future__ import annotations

import logging
from dataclasses import dataclass, field

from property_service.config import Settings, get_settings
from property_service.config.logging import setup_logging
from property_service.di.container import build_container

logger = logging.getLogger(__name__)

STARTUP_SEQUENCE: tuple[str, ...] = (
    "load_configuration",
    "initialize_logging",
    "connect_postgresql",
    "connect_redis",
    "run_migrations",
    "seed_lookups",
    "connect_rabbitmq",
    "fetch_jwks",
    "wire_di_container",
    "warm_caches",
)


@dataclass
class StartupBootstrap:
    settings: Settings
    completed_steps: list[str] = field(default_factory=list)

    async def run(self) -> None:
        self._step_load_configuration()
        self._step_initialize_logging()
        await self._step_connect_postgresql()
        await self._step_connect_redis()
        await self._step_run_migrations()
        await self._step_seed_lookups()
        await self._step_connect_rabbitmq()
        await self._step_fetch_jwks()
        self._step_wire_di_container()
        await self._step_warm_caches()

    def _record(self, step: str) -> None:
        self.completed_steps.append(step)
        logger.debug("startup_step_complete", extra={"step": step})

    def _step_load_configuration(self) -> None:
        _ = self.settings.app_name
        self._record("load_configuration")

    def _step_initialize_logging(self) -> None:
        setup_logging(self.settings.log_level)
        self._record("initialize_logging")

    async def _step_connect_postgresql(self) -> None:
        from sqlalchemy import text
        from property_service.infrastructure.persistence.database import get_session_factory

        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
        self._record("connect_postgresql")

    async def _step_connect_redis(self) -> None:
        if self.settings.cache_backend == "memory":
            self._record("connect_redis")
            return
        from property_service.infrastructure.cache.redis_client import get_redis_client

        redis = await get_redis_client()
        await redis.ping()
        self._record("connect_redis")

    async def _step_run_migrations(self) -> None:
        if not self.settings.run_migrations:
            return
        from property_service.infrastructure.persistence.database import init_db

        await init_db()
        self._record("run_migrations")

    async def _step_seed_lookups(self) -> None:
        if not self.settings.seed_lookups:
            return
        from scripts.seed_property_types import seed

        await seed()
        self._record("seed_lookups")

    async def _step_connect_rabbitmq(self) -> None:
        if self.settings.is_development:
            self._record("connect_rabbitmq")
            return
        try:
            import aio_pika

            connection = await aio_pika.connect_robust(self.settings.rabbitmq_url, timeout=5)
            await connection.close()
            self._record("connect_rabbitmq")
        except ImportError:
            logger.warning("aio_pika_not_installed_skipping_rabbitmq_check")
            self._record("connect_rabbitmq")
        except Exception:
            logger.warning("rabbitmq_connect_failed_startup_continues")
            self._record("connect_rabbitmq")

    async def _step_fetch_jwks(self) -> None:
        if not self.settings.jwks_url:
            return
        from property_service.application.security.jwt_validator import JwtValidator

        validator = JwtValidator()
        await validator.warm_jwks_cache()
        self._record("fetch_jwks")

    def _step_wire_di_container(self) -> None:
        build_container()
        self._record("wire_di_container")

    async def _step_warm_caches(self) -> None:
        from property_service.di.container import get_container

        try:
            await get_container().cache_manager.warm_lookup_caches()
        except Exception:
            logger.warning("lookup_cache_warm_failed")
        self._record("warm_caches")


async def bootstrap_application(settings: Settings | None = None) -> StartupBootstrap:
    bootstrap = StartupBootstrap(settings=settings or get_settings())
    await bootstrap.run()
    return bootstrap
