from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from property_service.domain.entities.property_building import PropertyBuilding
from property_service.domain.entities.property_document import PropertyDocument
from property_service.domain.entities.property_features import PropertyFeatures
from property_service.domain.entities.property_image import PropertyAmenity, PropertyImage, PropertyVideo
from property_service.domain.entities.property_listing import PropertyListing
from property_service.domain.entities.property_location import PropertyLocation
from property_service.domain.entities.property_ownership import OwnershipHistoryEntry, PropertyOwnership
from property_service.domain.entities.property_parcel import PropertyParcel
from property_service.domain.entities.property_pricing import PriceHistoryEntry, PropertyPricing
from property_service.domain.entities.property_version import (
    PropertyAuditLog,
    PropertyExternalSource,
    PropertyMetadata,
    StatusHistoryEntry,
)
from property_service.domain.enums.property_status import STATUS_TRANSITIONS, PropertyStatus
from property_service.domain.enums.property_visibility import PropertyVisibility
from property_service.domain.enums.source_type import SourceType
from property_service.domain.events import (
    DomainEvent,
    PropertyCreated,
    PropertyDeleted,
    PropertyDocumentsUpdated,
    PropertyImagesUpdated,
    PropertyLocationChanged,
    PropertyOwnershipChanged,
    PropertyPriceChanged,
    PropertyRestored,
    PropertyStatusChanged,
    PropertyUpdated,
)
from property_service.domain.exceptions import (
    ImmutableFieldError,
    InvalidStatusTransitionError,
    PropertyDeletedError,
    ValidationError,
)
from property_service.domain.services.property_validator import PropertyValidator
from property_service.domain.value_objects.property_classification import PropertyClassification
from property_service.domain.value_objects.property_code import PropertyCode
from property_service.domain.value_objects.slug import Slug


@dataclass
class Property:
    """Aggregate root for real estate assets."""

    id: UUID
    tenant_id: UUID
    property_code: PropertyCode
    slug: Slug
    title: str
    classification: PropertyClassification
    location: PropertyLocation
    created_by: UUID
    status: PropertyStatus = PropertyStatus.DRAFT
    visibility: PropertyVisibility = PropertyVisibility.PRIVATE
    description: str | None = None
    summary: str | None = None
    pricing: PropertyPricing = field(default_factory=PropertyPricing)
    parcel: PropertyParcel | None = None
    building: PropertyBuilding | None = None
    features: PropertyFeatures = field(default_factory=PropertyFeatures)
    amenities: list[PropertyAmenity] = field(default_factory=list)
    images: list[PropertyImage] = field(default_factory=list)
    videos: list[PropertyVideo] = field(default_factory=list)
    documents: list[PropertyDocument] = field(default_factory=list)
    listing: PropertyListing | None = None
    ownership: list[PropertyOwnership] = field(default_factory=list)
    ownership_history: list[OwnershipHistoryEntry] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: PropertyMetadata = field(default_factory=PropertyMetadata)
    external_sources: list[PropertyExternalSource] = field(default_factory=list)
    price_history: list[PriceHistoryEntry] = field(default_factory=list)
    status_history: list[StatusHistoryEntry] = field(default_factory=list)
    audit_logs: list[PropertyAuditLog] = field(default_factory=list)
    version: int = 1
    published_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = None
    updated_by: UUID | None = None
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    def collect_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def _raise(self, event: DomainEvent) -> None:
        event.aggregate_id = self.id
        event.tenant_id = self.tenant_id
        self._events.append(event)

    def _touch(self, actor_id: UUID) -> None:
        self.updated_at = datetime.now(timezone.utc)
        self.updated_by = actor_id
        self.version += 1

    def _ensure_not_deleted(self) -> None:
        if self.deleted_at is not None:
            raise PropertyDeletedError(self.id)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def active_images(self) -> list[PropertyImage]:
        return [img for img in self.images if img.deleted_at is None]

    @property
    def active_documents(self) -> list[PropertyDocument]:
        return [doc for doc in self.documents if doc.deleted_at is None]

    @classmethod
    def create(
        cls,
        *,
        tenant_id: UUID,
        property_code: PropertyCode,
        slug: Slug,
        title: str,
        classification: PropertyClassification,
        location: PropertyLocation,
        created_by: UUID,
        source: PropertyExternalSource,
        description: str | None = None,
        summary: str | None = None,
        pricing: PropertyPricing | None = None,
        building: PropertyBuilding | None = None,
        parcel: PropertyParcel | None = None,
        features: PropertyFeatures | None = None,
        amenities: list[PropertyAmenity] | None = None,
        tags: list[str] | None = None,
        status: PropertyStatus = PropertyStatus.DRAFT,
        visibility: PropertyVisibility = PropertyVisibility.PRIVATE,
    ) -> Property:
        PropertyValidator.validate_creation(
            classification=classification,
            location=location,
            pricing=pricing,
            building=building,
            parcel=parcel,
        )

        prop = cls(
            id=uuid4(),
            tenant_id=tenant_id,
            property_code=property_code,
            slug=slug,
            title=title.strip(),
            classification=classification,
            location=location,
            created_by=created_by,
            updated_by=created_by,
            description=description,
            summary=summary,
            pricing=pricing or PropertyPricing(),
            building=building,
            parcel=parcel,
            features=features or PropertyFeatures(),
            amenities=amenities or [],
            tags=tags or [],
            status=status,
            visibility=visibility,
            external_sources=[source],
        )

        if prop.building:
            prop.building.compute_building_age()
            prop.pricing.compute_price_per_sqm(prop.building.net_area_sqm)

        if prop.pricing.has_any_price() and not prop.pricing.currency:
            raise ValidationError("Currency is required when a price is set", code="CURRENCY_REQUIRED")

        prop._raise(PropertyCreated(
            property_id=prop.id,
            property_code=str(prop.property_code),
            slug=str(prop.slug),
            property_type=classification.property_type.value,
            property_category=classification.category.value,
            status=status.value,
            source_type=source.source_type.value,
            country_code=location.country_code,
            province=location.province,
            district=location.district,
            latitude=location.latitude,
            longitude=location.longitude,
            sale_price=prop.pricing.sale_price,
            currency=prop.pricing.currency,
            created_by=created_by,
        ))
        return prop

    def update_title(self, title: str, actor_id: UUID) -> None:
        self._ensure_not_deleted()
        new_title = title.strip()
        if new_title == self.title:
            return
        old = self.title
        self.title = new_title
        self._touch(actor_id)
        self._raise(PropertyUpdated(
            property_id=self.id,
            property_code=str(self.property_code),
            version=self.version,
            changed_fields=["title"],
            changes={"title": {"old": old, "new": new_title}},
            updated_by=actor_id,
        ))

    def update_description(self, description: str | None, actor_id: UUID) -> None:
        self._ensure_not_deleted()
        if description == self.description:
            return
        old = self.description
        self.description = description
        self._touch(actor_id)
        self._raise(PropertyUpdated(
            property_id=self.id,
            property_code=str(self.property_code),
            version=self.version,
            changed_fields=["description"],
            changes={"description": {"old": old, "new": description}},
            updated_by=actor_id,
        ))

    def update_pricing(self, pricing: PropertyPricing, actor_id: UUID, *, reason: str | None = None) -> None:
        self._ensure_not_deleted()
        PropertyValidator.validate_pricing(pricing, self.status)

        changes: dict[str, object] = {}
        changed_fields: list[str] = []

        for price_type, old_val, new_val in [
            ("sale", self.pricing.sale_price, pricing.sale_price),
            ("rental", self.pricing.rental_price, pricing.rental_price),
            ("maintenance", self.pricing.maintenance_fee, pricing.maintenance_fee),
        ]:
            if old_val != new_val:
                changed_fields.append(f"pricing.{price_type}")
                changes[f"pricing.{price_type}"] = {"old": old_val, "new": new_val}
                self.price_history.append(PriceHistoryEntry(
                    price_type=price_type,
                    old_amount=old_val,
                    new_amount=new_val,
                    currency=pricing.currency,
                    changed_by=actor_id,
                    change_reason=reason,
                ))
                self._raise(PropertyPriceChanged(
                    property_id=self.id,
                    property_code=str(self.property_code),
                    price_type=price_type,
                    old_amount=old_val,
                    new_amount=new_val,
                    currency=pricing.currency,
                    changed_by=actor_id,
                    change_reason=reason,
                ))

        if not changed_fields:
            return

        self.pricing = pricing
        net_area = self.building.net_area_sqm if self.building else None
        self.pricing.compute_price_per_sqm(net_area)
        self._touch(actor_id)
        self._raise(PropertyUpdated(
            property_id=self.id,
            property_code=str(self.property_code),
            version=self.version,
            changed_fields=changed_fields,
            changes=changes,
            updated_by=actor_id,
        ))

    def update_location(self, location: PropertyLocation, actor_id: UUID, *, geocoded: bool = False) -> None:
        self._ensure_not_deleted()
        PropertyValidator.validate_location(location)

        old_location = self._location_snapshot()
        if self._locations_equal(old_location, self._location_snapshot_from(location)):
            return

        self.location = location
        self._touch(actor_id)
        self._raise(PropertyLocationChanged(
            property_id=self.id,
            property_code=str(self.property_code),
            old_location=old_location,
            new_location=self._location_snapshot(),
            geocoded=geocoded,
            changed_by=actor_id,
        ))
        self._raise(PropertyUpdated(
            property_id=self.id,
            property_code=str(self.property_code),
            version=self.version,
            changed_fields=["location"],
            changes={"location": {"old": old_location, "new": self._location_snapshot()}},
            updated_by=actor_id,
        ))

    def change_status(self, new_status: PropertyStatus, actor_id: UUID, *, reason: str | None = None) -> None:
        self._ensure_not_deleted()
        if new_status == self.status:
            return

        allowed = STATUS_TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed:
            raise InvalidStatusTransitionError(self.status.value, new_status.value)

        PropertyValidator.validate_status_transition(
            self.status, new_status, self.pricing, self.active_images, self.location,
        )

        old_status = self.status
        self.status = new_status
        self.status_history.append(StatusHistoryEntry(
            old_status=old_status.value,
            new_status=new_status.value,
            changed_by=actor_id,
            reason=reason,
        ))

        if new_status in (PropertyStatus.ACTIVE, PropertyStatus.LISTED) and self.published_at is None:
            self.published_at = datetime.now(timezone.utc)

        self._touch(actor_id)
        self._raise(PropertyStatusChanged(
            property_id=self.id,
            property_code=str(self.property_code),
            old_status=old_status.value,
            new_status=new_status.value,
            reason=reason,
            changed_by=actor_id,
        ))

    def soft_delete(self, actor_id: UUID) -> None:
        if self.deleted_at is not None:
            return
        self.deleted_at = datetime.now(timezone.utc)
        old_status = self.status
        self.status = PropertyStatus.DELETED
        self.status_history.append(StatusHistoryEntry(
            old_status=old_status.value,
            new_status=PropertyStatus.DELETED.value,
            changed_by=actor_id,
            reason="soft delete",
        ))
        self._touch(actor_id)
        self._raise(PropertyDeleted(
            property_id=self.id,
            property_code=str(self.property_code),
            deleted_by=actor_id,
        ))

    def restore(self, actor_id: UUID) -> None:
        if self.deleted_at is None:
            return
        self.deleted_at = None
        self.status = PropertyStatus.DRAFT
        self._touch(actor_id)
        self._raise(PropertyRestored(
            property_id=self.id,
            property_code=str(self.property_code),
            restored_by=actor_id,
        ))

    def add_image(self, image: PropertyImage, actor_id: UUID) -> None:
        self._ensure_not_deleted()
        if image.is_primary:
            for img in self.active_images:
                img.is_primary = False
        elif not self.active_images:
            image.is_primary = True

        self.images.append(image)
        PropertyValidator.validate_single_primary(self.images)
        self._touch(actor_id)
        self._raise(PropertyImagesUpdated(
            property_id=self.id,
            action="added",
            image_ids=[image.id],
            primary_image_id=next((i.id for i in self.active_images if i.is_primary), None),
            total_images=len(self.active_images),
            updated_by=actor_id,
        ))

    def remove_image(self, image_id: UUID, actor_id: UUID) -> None:
        self._ensure_not_deleted()
        image = next((i for i in self.images if i.id == image_id and i.deleted_at is None), None)
        if image is None:
            raise ValidationError(f"Image {image_id} not found", code="IMAGE_NOT_FOUND")
        image.deleted_at = datetime.now(timezone.utc)
        was_primary = image.is_primary
        if was_primary and self.active_images:
            self.active_images[0].is_primary = True
        self._touch(actor_id)
        self._raise(PropertyImagesUpdated(
            property_id=self.id,
            action="removed",
            image_ids=[image_id],
            primary_image_id=next((i.id for i in self.active_images if i.is_primary), None),
            total_images=len(self.active_images),
            updated_by=actor_id,
        ))

    def reorder_images(self, image_ids: list[UUID], actor_id: UUID) -> None:
        self._ensure_not_deleted()
        active = {img.id: img for img in self.active_images}
        if set(image_ids) != set(active.keys()):
            raise ValidationError("image_ids must match active images", code="IMAGE_REORDER_MISMATCH")
        for order, image_id in enumerate(image_ids):
            active[image_id].sort_order = order
        self._touch(actor_id)
        self._raise(PropertyImagesUpdated(
            property_id=self.id,
            action="reordered",
            image_ids=image_ids,
            primary_image_id=next((i.id for i in self.active_images if i.is_primary), None),
            total_images=len(self.active_images),
            updated_by=actor_id,
        ))

    def add_document(self, document: PropertyDocument, actor_id: UUID) -> None:
        self._ensure_not_deleted()
        self.documents.append(document)
        self._touch(actor_id)
        self._raise(PropertyDocumentsUpdated(
            property_id=self.id,
            action="added",
            document_ids=[document.id],
            document_types=[document.document_type.value],
            updated_by=actor_id,
        ))

    def remove_document(self, document_id: UUID, actor_id: UUID) -> None:
        self._ensure_not_deleted()
        document = next((d for d in self.documents if d.id == document_id and d.deleted_at is None), None)
        if document is None:
            raise ValidationError(f"Document {document_id} not found", code="DOCUMENT_NOT_FOUND")
        document.deleted_at = datetime.now(timezone.utc)
        self._touch(actor_id)
        self._raise(PropertyDocumentsUpdated(
            property_id=self.id,
            action="removed",
            document_ids=[document_id],
            document_types=[document.document_type.value],
            updated_by=actor_id,
        ))

    def verify_document(self, document_id: UUID, actor_id: UUID) -> None:
        self._ensure_not_deleted()
        document = next((d for d in self.documents if d.id == document_id and d.deleted_at is None), None)
        if document is None:
            raise ValidationError(f"Document {document_id} not found", code="DOCUMENT_NOT_FOUND")
        document.verified = True
        document.verified_at = datetime.now(timezone.utc)
        document.verified_by = actor_id
        self._touch(actor_id)
        self._raise(PropertyDocumentsUpdated(
            property_id=self.id,
            action="verified",
            document_ids=[document_id],
            document_types=[document.document_type.value],
            updated_by=actor_id,
        ))

    def add_ownership(self, ownership: PropertyOwnership, actor_id: UUID) -> None:
        self._ensure_not_deleted()
        PropertyValidator.validate_ownership(self.ownership, ownership)
        self.ownership.append(ownership)
        self._touch(actor_id)
        self._raise(PropertyOwnershipChanged(
            property_id=self.id,
            action="added",
            current_owners=self._ownership_snapshot(),
            changed_by=actor_id,
        ))

    def set_tags(self, tags: list[str], actor_id: UUID) -> None:
        self._ensure_not_deleted()
        normalized = list(dict.fromkeys(t.strip() for t in tags if t.strip()))[:20]
        if normalized == self.tags:
            return
        old = self.tags
        self.tags = normalized
        self._touch(actor_id)
        self._raise(PropertyUpdated(
            property_id=self.id,
            property_code=str(self.property_code),
            version=self.version,
            changed_fields=["tags"],
            changes={"tags": {"old": old, "new": normalized}},
            updated_by=actor_id,
        ))

    def set_amenities(self, amenities: list[PropertyAmenity], actor_id: UUID) -> None:
        self._ensure_not_deleted()
        self.amenities = amenities
        self._touch(actor_id)
        self._raise(PropertyUpdated(
            property_id=self.id,
            property_code=str(self.property_code),
            version=self.version,
            changed_fields=["amenities"],
            changes={"amenities": {"old": [], "new": [a.amenity_code for a in amenities]}},
            updated_by=actor_id,
        ))

    def _location_snapshot(self) -> dict[str, object]:
        return self._location_snapshot_from(self.location)

    @staticmethod
    def _location_snapshot_from(loc: PropertyLocation) -> dict[str, object]:
        return {
            "country_code": loc.country_code,
            "province": loc.province,
            "district": loc.district,
            "neighborhood": loc.neighborhood,
            "latitude": str(loc.latitude) if loc.latitude is not None else None,
            "longitude": str(loc.longitude) if loc.longitude is not None else None,
        }

    @staticmethod
    def _locations_equal(a: dict[str, object], b: dict[str, object]) -> bool:
        return a == b

    def _ownership_snapshot(self) -> list[dict[str, object]]:
        return [
            {
                "owner_name": o.owner_name,
                "ownership_percentage": str(o.ownership_percentage),
                "is_current": o.is_current,
            }
            for o in self.ownership if o.is_current
        ]

    def assert_version(self, expected: int) -> None:
        from property_service.domain.exceptions import ConcurrencyConflictError
        if self.version != expected:
            raise ConcurrencyConflictError(self.id, expected, self.version)

    def reject_property_code_change(self, new_code: PropertyCode) -> None:
        if new_code != self.property_code:
            raise ImmutableFieldError("property_code")
