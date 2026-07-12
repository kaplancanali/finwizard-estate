"""Entity relationship registry — mirrors docs/architecture/04-entity-relationship-diagram.md."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Cardinality = Literal["1:1", "1:N", "N:1", "lookup"]


@dataclass(frozen=True)
class EntityRelationship:
    parent: str
    child: str
    cardinality: Cardinality
    fk_column: str | None = None
    notes: str = ""


# Core ERD — Property aggregate root and related tables
PROPERTY_ERD: tuple[EntityRelationship, ...] = (
    EntityRelationship("properties", "property_addresses", "1:1", "property_id"),
    EntityRelationship("properties", "property_parcels", "1:1", "property_id"),
    EntityRelationship("properties", "property_buildings", "1:1", "property_id"),
    EntityRelationship("properties", "property_features", "1:1", "property_id"),
    EntityRelationship("properties", "property_metadata", "1:1", "property_id"),
    EntityRelationship("properties", "property_listings", "1:1", "property_id"),
    EntityRelationship("properties", "property_amenities", "1:N", "property_id"),
    EntityRelationship("properties", "property_images", "1:N", "property_id"),
    EntityRelationship("properties", "property_videos", "1:N", "property_id"),
    EntityRelationship("properties", "property_documents", "1:N", "property_id"),
    EntityRelationship("properties", "property_ownership", "1:N", "property_id"),
    EntityRelationship("properties", "property_ownership_history", "1:N", "property_id"),
    EntityRelationship("properties", "property_tags", "1:N", "property_id"),
    EntityRelationship("properties", "property_external_sources", "1:N", "property_id"),
    EntityRelationship("properties", "property_price_history", "1:N", "property_id"),
    EntityRelationship("properties", "property_status_history", "1:N", "property_id"),
    EntityRelationship("properties", "property_versions", "1:N", "property_id"),
    EntityRelationship("properties", "property_audit_logs", "1:N", "property_id"),
    EntityRelationship("properties", "outbox_events", "1:N", "aggregate_id", notes="logical, no DB FK"),
    EntityRelationship("property_types", "properties", "1:N", "property_type", notes="FK to property_types.code"),
    EntityRelationship("amenity_definitions", "property_amenities", "1:N", "amenity_code"),
)

AGGREGATE_ENTITIES: frozenset[str] = frozenset(
    {
        "property_addresses",
        "property_parcels",
        "property_buildings",
        "property_features",
        "property_metadata",
        "property_listings",
        "property_amenities",
        "property_images",
        "property_videos",
        "property_documents",
        "property_ownership",
        "property_tags",
        "property_external_sources",
    }
)

HISTORY_ENTITIES: frozenset[str] = frozenset(
    {
        "property_price_history",
        "property_status_history",
        "property_ownership_history",
    }
)

INFRASTRUCTURE_ENTITIES: frozenset[str] = frozenset({"property_versions", "property_audit_logs", "outbox_events"})

LOOKUP_ENTITIES: frozenset[str] = frozenset({"property_types", "amenity_definitions"})

ALL_ERD_TABLES: frozenset[str] = frozenset(
    {"properties"}
    | AGGREGATE_ENTITIES
    | HISTORY_ENTITIES
    | INFRASTRUCTURE_ENTITIES
    | LOOKUP_ENTITIES
)

ORM_TABLE_TO_MODEL: dict[str, str] = {
    "properties": "PropertyModel",
    "property_addresses": "PropertyAddressModel",
    "property_parcels": "PropertyParcelModel",
    "property_buildings": "PropertyBuildingModel",
    "property_features": "PropertyFeaturesModel",
    "property_metadata": "PropertyMetadataModel",
    "property_listings": "PropertyListingModel",
    "property_amenities": "PropertyAmenityModel",
    "property_images": "PropertyImageModel",
    "property_videos": "PropertyVideoModel",
    "property_documents": "PropertyDocumentModel",
    "property_ownership": "PropertyOwnershipModel",
    "property_ownership_history": "PropertyOwnershipHistoryModel",
    "property_tags": "PropertyTagModel",
    "property_external_sources": "PropertyExternalSourceModel",
    "property_price_history": "PropertyPriceHistoryModel",
    "property_status_history": "PropertyStatusHistoryModel",
    "property_versions": "PropertyVersionModel",
    "property_audit_logs": "PropertyAuditLogModel",
    "outbox_events": "OutboxEventModel",
    "property_types": "PropertyTypeLookupModel",
    "amenity_definitions": "AmenityDefinitionModel",
}
