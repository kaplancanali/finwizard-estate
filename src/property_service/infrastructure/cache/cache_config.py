from __future__ import annotations

import hashlib
import json
from uuid import UUID

from property_service.application.dto.property_search_dto import PropertySearchCriteria

# TTLs in seconds (docs/architecture/13-cache-strategy.md)
TTL_PROPERTY_DETAIL = 900
TTL_PROPERTY_CODE = 1800
TTL_PROPERTY_SLUG = 1800
TTL_PROPERTY_SEARCH = 300
TTL_PROPERTY_NEARBY = 300
TTL_PROPERTY_STATS = 1800
TTL_PROPERTY_METADATA = 900
TTL_LOOKUP = 86400
TTL_IDEMPOTENCY = 86400
TTL_RATE_LIMIT = 60
TTL_JWKS = 3600
TTL_STAMPEDE_LOCK = 5


def property_detail_key(property_id: UUID) -> str:
    return f"property:detail:{property_id}"


def property_metadata_key(property_id: UUID) -> str:
    return f"property:metadata:{property_id}"


def property_code_key(tenant_id: UUID, code: str) -> str:
    return f"property:code:{tenant_id}:{code}"


def property_slug_key(tenant_id: UUID, slug: str) -> str:
    return f"property:slug:{tenant_id}:{slug}"


def property_stats_key(tenant_id: UUID) -> str:
    return f"property:stats:{tenant_id}"


def property_search_pattern(tenant_id: UUID) -> str:
    return f"property:search:{tenant_id}:*"


def property_nearby_pattern(tenant_id: UUID, geohash: str) -> str:
    return f"property:nearby:{tenant_id}:{geohash}:*"


def property_nearby_key(tenant_id: UUID, geohash: str, radius: int) -> str:
    return f"property:nearby:{tenant_id}:{geohash}:{radius}"


def lookup_types_key() -> str:
    return "property:types"


def lookup_amenities_key() -> str:
    return "property:amenities"


def jwks_cache_key() -> str:
    return "jwks:keys"


def stampede_lock_key(property_id: UUID) -> str:
    return f"lock:property:detail:{property_id}"


def search_cache_key(tenant_id: UUID, criteria_hash: str) -> str:
    return f"property:search:{tenant_id}:{criteria_hash}"


def hash_search_criteria(criteria: PropertySearchCriteria) -> str:
    payload = json.dumps(
        {
            "query": criteria.query,
            "filters": criteria.filters_dict,
            "geo": criteria.geo_dict,
            "sort": criteria.sort_list,
            "page": criteria.page,
            "page_size": criteria.page_size,
            "include_facets": criteria.include_facets,
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
