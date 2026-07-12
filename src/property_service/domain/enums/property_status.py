from __future__ import annotations

from property_service.domain.enums._base import StrEnum


class PropertyStatus(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    LISTED = "listed"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DELETED = "deleted"


# Valid status transitions: from_status -> set of allowed to_status values.
STATUS_TRANSITIONS: dict[PropertyStatus, frozenset[PropertyStatus]] = {
    PropertyStatus.DRAFT: frozenset({
        PropertyStatus.PENDING,
        PropertyStatus.ACTIVE,
        PropertyStatus.ARCHIVED,
        PropertyStatus.DELETED,
    }),
    PropertyStatus.PENDING: frozenset({
        PropertyStatus.DRAFT,
        PropertyStatus.ACTIVE,
        PropertyStatus.ARCHIVED,
        PropertyStatus.DELETED,
    }),
    PropertyStatus.ACTIVE: frozenset({
        PropertyStatus.LISTED,
        PropertyStatus.INACTIVE,
        PropertyStatus.ARCHIVED,
        PropertyStatus.DELETED,
    }),
    PropertyStatus.LISTED: frozenset({
        PropertyStatus.ACTIVE,
        PropertyStatus.INACTIVE,
        PropertyStatus.ARCHIVED,
        PropertyStatus.DELETED,
    }),
    PropertyStatus.INACTIVE: frozenset({
        PropertyStatus.DRAFT,
        PropertyStatus.ACTIVE,
        PropertyStatus.LISTED,
        PropertyStatus.ARCHIVED,
        PropertyStatus.DELETED,
    }),
    PropertyStatus.ARCHIVED: frozenset({
        PropertyStatus.DELETED,
    }),
    PropertyStatus.DELETED: frozenset({
        PropertyStatus.DRAFT,  # restore
    }),
}
