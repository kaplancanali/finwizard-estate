from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from property_service.application.auth_context import AuthContext
from property_service.config import get_settings
from property_service.domain.exceptions import RateLimitExceededError
from property_service.presentation.errors.error_registry import http_status_for_code
from property_service.presentation.errors.response_builder import build_error_payload


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter (in-memory; Redis-backed in production)."""

    def __init__(self, app) -> None:
        super().__init__(app)
        settings = get_settings()
        self._authenticated_limit = settings.rate_limit_per_minute
        self._unauthenticated_limit = settings.rate_limit_unauthenticated_per_minute
        self._window_seconds = 60
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _rate_limit_key(self, request: Request) -> tuple[str, int]:
        auth: AuthContext | None = getattr(request.state, "auth", None)
        if auth and auth.client_id:
            if auth.actor_type == "api_key":
                return f"ratelimit:apikey:{auth.client_id}", self._authenticated_limit
            return f"ratelimit:user:{auth.client_id}", self._authenticated_limit

        forwarded = request.headers.get("X-Forwarded-For")
        client = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
        return f"ratelimit:ip:{client}", self._unauthenticated_limit

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path.startswith("/health") or request.url.path == "/metrics":
            return await call_next(request)

        now = time.monotonic()
        key, limit = self._rate_limit_key(request)
        bucket = self._hits[key]
        while bucket and now - bucket[0] > self._window_seconds:
            bucket.popleft()

        if len(bucket) >= limit:
            exc = RateLimitExceededError(retry_after=self._window_seconds)
            response = JSONResponse(
                status_code=http_status_for_code(exc.code),
                content=build_error_payload(request, code=exc.code, message=exc.message),
                headers={"Retry-After": str(exc.retry_after)},
            )
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(self._window_seconds)
            return response

        bucket.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - len(bucket)))
        response.headers["X-RateLimit-Reset"] = str(self._window_seconds)
        return response
