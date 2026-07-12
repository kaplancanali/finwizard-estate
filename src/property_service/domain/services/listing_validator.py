from __future__ import annotations

import re
from urllib.parse import urlparse

from property_service.domain.exceptions import ValidationError
from property_service.domain.services.url_safety import assert_public_http_url

_LISTING_URL = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)

SUPPORTED_LISTING_PROVIDERS: frozenset[str] = frozenset({
    "stub",
    "sahibinden",
    "emlakjet",
    "hepsiemlak",
})


class ListingValidator:
    @staticmethod
    def validate_url(url: str) -> str:
        stripped = url.strip()
        if not _LISTING_URL.match(stripped):
            raise ValidationError(
                "Invalid listing URL format",
                code="INVALID_LISTING_URL",
                field="source_reference",
            )
        return assert_public_http_url(stripped)

    @staticmethod
    def resolve_provider(url: str) -> str:
        host = urlparse(url).netloc.lower()
        for provider in SUPPORTED_LISTING_PROVIDERS:
            if provider in host:
                return provider
        if host:
            return host.split(".")[0]
        return "unknown"

    @staticmethod
    def assert_supported_provider(provider: str) -> None:
        if provider not in SUPPORTED_LISTING_PROVIDERS and provider not in {"unknown"}:
            raise ValidationError(
                f"Unsupported listing provider '{provider}'",
                code="UNSUPPORTED_PROVIDER",
                field="source_reference",
            )
