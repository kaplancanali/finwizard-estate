from __future__ import annotations

from property_service.domain.events.base import DomainEvent
from property_service.domain.events.catalog import (
    CONSUMER_QUEUE_BINDINGS,
    DEAD_LETTER_EXCHANGE,
    EVENT_CATALOG,
    EVENT_EXCHANGE,
    EVENT_SOURCE,
    MAX_OUTBOX_RETRIES,
    OUTBOX_BATCH_SIZE,
)
from property_service.domain.events.property_created import PropertyCreated
from property_service.domain.events.property_deleted import PropertyDeleted
from property_service.domain.events.property_documents_updated import PropertyDocumentsUpdated
from property_service.domain.events.property_images_updated import PropertyImagesUpdated
from property_service.domain.events.property_imported import PropertyImported
from property_service.domain.events.property_listed import PropertyListed
from property_service.domain.events.property_location_changed import PropertyLocationChanged
from property_service.domain.events.property_ownership_changed import PropertyOwnershipChanged
from property_service.domain.events.property_price_changed import PropertyPriceChanged
from property_service.domain.events.property_restored import PropertyRestored
from property_service.domain.events.property_status_changed import PropertyStatusChanged
from property_service.domain.events.property_updated import PropertyUpdated
from property_service.domain.events.property_version_created import PropertyVersionCreated

__all__ = [
    "CONSUMER_QUEUE_BINDINGS",
    "DEAD_LETTER_EXCHANGE",
    "EVENT_CATALOG",
    "EVENT_EXCHANGE",
    "EVENT_SOURCE",
    "MAX_OUTBOX_RETRIES",
    "OUTBOX_BATCH_SIZE",
    "DomainEvent",
    "PropertyCreated",
    "PropertyDeleted",
    "PropertyDocumentsUpdated",
    "PropertyImagesUpdated",
    "PropertyImported",
    "PropertyListed",
    "PropertyLocationChanged",
    "PropertyOwnershipChanged",
    "PropertyPriceChanged",
    "PropertyRestored",
    "PropertyStatusChanged",
    "PropertyUpdated",
    "PropertyVersionCreated",
]
