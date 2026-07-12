from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from property_service.config import get_settings
from property_service.presentation.api.v1.router import api_v1_router
from property_service.presentation.exception_handlers import register_exception_handlers
from property_service.presentation.health import health_router, mark_startup_complete
from property_service.presentation.middleware.authentication import AuthenticationMiddleware
from property_service.presentation.middleware.correlation_id import CorrelationIdMiddleware
from property_service.presentation.middleware.idempotency import IdempotencyMiddleware
from property_service.presentation.middleware.rate_limiting import RateLimitingMiddleware
from property_service.presentation.middleware.request_logging import RequestLoggingMiddleware
from property_service.presentation.middleware.security_headers import SecurityHeadersMiddleware


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from property_service.architecture.startup import bootstrap_application
        from property_service.presentation.health import mark_startup_complete

        await bootstrap_application(settings)
        mark_startup_complete()
        yield
        from property_service.infrastructure.persistence.database import close_db

        await close_db()
        if settings.cache_backend == "redis":
            from property_service.infrastructure.cache.redis_client import close_redis_client

            await close_redis_client()

    app = FastAPI(
        title="FINWARD Property Service",
        version="0.1.0",
        description=(
            "Property Service API. Client retry guidance: "
            "409 concurrency conflicts — refetch and retry; "
            "409 idempotency conflicts — use a new Idempotency-Key; "
            "429/500/503 — retry with exponential backoff (max 3); "
            "400/401/403/404/422 — do not retry."
        ),
        docs_url="/api/v1/docs" if settings.debug else None,
        openapi_url="/api/v1/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(IdempotencyMiddleware)
    app.add_middleware(RateLimitingMiddleware)
    app.add_middleware(AuthenticationMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    register_exception_handlers(app)
    app.include_router(health_router)

    @app.get("/metrics")
    async def metrics():
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
        from starlette.responses import Response

        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
