from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from property_service.domain.exceptions import ValidationError

_BLOCKED_HOSTS = frozenset({"localhost", "metadata", "metadata.google.internal"})


def assert_public_http_url(url: str) -> str:
    """Block SSRF targets (localhost, metadata endpoints, private IP ranges)."""
    parsed = urlparse(url.strip())
    host = parsed.hostname
    if not host:
        raise ValidationError("Invalid URL host", code="INVALID_LISTING_URL", field="source_reference")

    lowered = host.lower()
    if lowered in _BLOCKED_HOSTS or lowered.endswith(".local"):
        raise ValidationError("URL host not allowed", code="INVALID_LISTING_URL", field="source_reference")

    try:
        for info in socket.getaddrinfo(host, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise ValidationError(
                    "URL resolves to a private network address",
                    code="INVALID_LISTING_URL",
                    field="source_reference",
                )
    except socket.gaierror:
        pass

    return url
