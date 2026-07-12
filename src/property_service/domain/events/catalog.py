"""Event catalog — mirrors docs/architecture/06-event-definitions.md."""

from __future__ import annotations

from dataclasses import dataclass

EVENT_EXCHANGE = "property.events"
DEAD_LETTER_EXCHANGE = "property.events.dlx"
EVENT_SOURCE = "property-service"
MAX_OUTBOX_RETRIES = 5
OUTBOX_BATCH_SIZE = 100


@dataclass(frozen=True)
class EventDefinition:
    name: str
    cloud_events_type: str
    routing_key: str
    version: int = 1
    description: str = ""


def _def(name: str, slug: str, description: str = "") -> EventDefinition:
    version = 1
    return EventDefinition(
        name=name,
        cloud_events_type=f"com.finward.{slug}.v{version}",
        routing_key=f"{slug}.v{version}",
        version=version,
        description=description,
    )


EVENT_CATALOG: dict[str, EventDefinition] = {
    d.name: d
    for d in (
        _def("PropertyCreated", "property.created", "New property registered"),
        _def("PropertyUpdated", "property.updated", "Any field change on property"),
        _def("PropertyDeleted", "property.deleted", "Soft delete"),
        _def("PropertyImported", "property.imported", "Bulk import job completed"),
        _def("PropertyPriceChanged", "property.price_changed", "Sale, rental, or maintenance fee change"),
        _def("PropertyLocationChanged", "property.location_changed", "Address or coordinates change"),
        _def("PropertyStatusChanged", "property.status_changed", "Status state machine transition"),
        _def("PropertyImagesUpdated", "property.images_updated", "Image add, remove, reorder, or primary change"),
        _def("PropertyDocumentsUpdated", "property.documents_updated", "Document add, remove, or verify"),
        _def("PropertyOwnershipChanged", "property.ownership_changed", "Ownership record add/update/release"),
        _def("PropertyRestored", "property.restored", "Soft-deleted property restored"),
        _def("PropertyListed", "property.listed", "Property linked to external listing"),
        _def("PropertyVersionCreated", "property.version_created", "Immutable version snapshot created"),
    )
}

CONSUMER_QUEUE_BINDINGS: dict[str, list[str]] = {
    "valuation.property.events": ["property.price_changed.v1"],
    "risk.property.events": ["property.location_changed.v1"],
    "search.property.events": ["property.*.v1"],
    "notification.property.events": [
        "property.status_changed.v1",
        "property.created.v1",
    ],
}
