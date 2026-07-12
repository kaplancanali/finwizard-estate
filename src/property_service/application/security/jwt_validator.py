from __future__ import annotations

from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from property_service.config import get_settings
from property_service.domain.exceptions import AuthenticationError


class JwtValidator:
    """Validates platform-issued JWTs (HS256 dev / RS256 via JWKS in production)."""

    def __init__(self) -> None:
        self._jwks_cache: dict[str, Any] | None = None

    def decode(self, token: str) -> dict[str, Any]:
        settings = get_settings()
        options = {"verify_aud": bool(settings.jwt_audience)}
        decode_kwargs: dict[str, Any] = {
            "algorithms": [settings.jwt_algorithm],
            "options": options,
        }
        if settings.jwt_audience:
            decode_kwargs["audience"] = settings.jwt_audience
        if settings.jwt_issuer:
            decode_kwargs["issuer"] = settings.jwt_issuer

        if settings.jwt_algorithm.upper().startswith("RS") and settings.jwks_url:
            key = self._resolve_jwks_key(token)
            return jwt.decode(token, key, **decode_kwargs)

        return jwt.decode(token, settings.jwt_secret, **decode_kwargs)

    def _resolve_jwks_key(self, token: str) -> dict[str, Any]:
        settings = get_settings()
        if not settings.jwks_url:
            raise AuthenticationError("JWKS URL not configured")
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        keys = self._load_jwks()
        for entry in keys.get("keys", []):
            if kid is None or entry.get("kid") == kid:
                return entry
        raise AuthenticationError("JWT signing key not found in JWKS")

    async def _load_jwks(self) -> dict[str, Any]:
        if self._jwks_cache is not None:
            return self._jwks_cache
        settings = get_settings()
        try:
            from property_service.infrastructure.cache.property_cache import RedisPropertyCache

            cache = RedisPropertyCache()
            cached = await cache.get_jwks()
            if cached:
                self._jwks_cache = cached
                return cached
        except Exception:
            pass
        try:
            import httpx

            response = httpx.get(settings.jwks_url, timeout=5.0)
            response.raise_for_status()
            self._jwks_cache = response.json()
            try:
                from property_service.infrastructure.cache.property_cache import RedisPropertyCache

                await RedisPropertyCache().set_jwks(self._jwks_cache, ttl=3600)
            except Exception:
                pass
            return self._jwks_cache
        except Exception as exc:
            raise AuthenticationError("Unable to load JWKS") from exc

    def parse_uuid(self, value: object, *, field: str) -> UUID:
        try:
            return UUID(str(value))
        except (TypeError, ValueError) as exc:
            raise AuthenticationError(f"Invalid JWT claim '{field}'") from exc

    def safe_decode(self, token: str) -> dict[str, Any] | None:
        try:
            return self.decode(token)
        except (JWTError, AuthenticationError):
            return None

    async def warm_jwks_cache(self) -> None:
        settings = get_settings()
        if not settings.jwks_url:
            return
        await self._load_jwks()
