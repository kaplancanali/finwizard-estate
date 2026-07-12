from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

JSONB = JSON  # cross-database JSON column

from property_service.infrastructure.persistence.database import (
    Base,
    PROPERTY_SCHEMA,
    fk_target,
    uuid_pk,
)

_TABLE_KWARGS = {"schema": PROPERTY_SCHEMA} if PROPERTY_SCHEMA else {}


class PropertyModel(Base):
    __tablename__ = "properties"
    __table_args__ = (
        UniqueConstraint("tenant_id", "property_code", name="uq_properties_tenant_code"),
        UniqueConstraint("tenant_id", "slug", name="uq_properties_tenant_slug"),
        CheckConstraint(
            "latitude IS NULL OR (latitude BETWEEN -90 AND 90)",
            name="ck_properties_latitude",
        ),
        CheckConstraint(
            "longitude IS NULL OR (longitude BETWEEN -180 AND 180)",
            name="ck_properties_longitude",
        ),
        CheckConstraint("version > 0", name="ck_properties_version"),
        Index("ix_properties_tenant_status", "tenant_id", "status"),
        Index("ix_properties_created_at", "created_at"),
        Index("ix_properties_type_location", "property_type", "country_code", "province", "district"),
        _TABLE_KWARGS,
    )

    id: Mapped[UUID] = uuid_pk()
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    property_code: Mapped[str] = mapped_column(String(32), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(String(1000))
    property_type: Mapped[str] = mapped_column(
        String(50),
        ForeignKey(fk_target("property_types", "code")),
        nullable=False,
    )
    property_category: Mapped[str] = mapped_column(String(50), nullable=False)
    property_subtype: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="private")
    sale_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    rental_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    maintenance_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(3))
    price_on_request: Mapped[bool] = mapped_column(Boolean, default=False)
    price_per_sqm: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    province: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    neighborhood: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    geohash: Mapped[Optional[str]] = mapped_column(String(12))
    net_area_sqm: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), index=True)
    gross_area_sqm: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    room_count: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), index=True)
    bathroom_count: Mapped[Optional[int]] = mapped_column(SmallInteger, index=True)
    construction_year: Mapped[Optional[int]] = mapped_column(SmallInteger, index=True)
    floor_number: Mapped[Optional[int]] = mapped_column(SmallInteger)
    parking_count: Mapped[Optional[int]] = mapped_column(SmallInteger)
    has_elevator: Mapped[Optional[bool]] = mapped_column(Boolean)
    heating_type: Mapped[Optional[str]] = mapped_column(String(50))
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    created_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    updated_by: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True))

    address: Mapped["PropertyAddressModel | None"] = relationship(back_populates="property", uselist=False, cascade="all, delete-orphan")
    building: Mapped["PropertyBuildingModel | None"] = relationship(back_populates="property", uselist=False, cascade="all, delete-orphan")
    features: Mapped["PropertyFeaturesModel | None"] = relationship(back_populates="property", uselist=False, cascade="all, delete-orphan")
    parcel: Mapped["PropertyParcelModel | None"] = relationship(back_populates="property", uselist=False, cascade="all, delete-orphan")
    metadata_row: Mapped["PropertyMetadataModel | None"] = relationship(back_populates="property", uselist=False, cascade="all, delete-orphan")
    listing: Mapped["PropertyListingModel | None"] = relationship(back_populates="property", uselist=False, cascade="all, delete-orphan")
    images: Mapped[list["PropertyImageModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    videos: Mapped[list["PropertyVideoModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    documents: Mapped[list["PropertyDocumentModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    amenities: Mapped[list["PropertyAmenityModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    tags: Mapped[list["PropertyTagModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    ownership: Mapped[list["PropertyOwnershipModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    ownership_history: Mapped[list["PropertyOwnershipHistoryModel"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    external_sources: Mapped[list["PropertyExternalSourceModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    price_history: Mapped[list["PropertyPriceHistoryModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    status_history: Mapped[list["PropertyStatusHistoryModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    audit_logs: Mapped[list["PropertyAuditLogModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    versions: Mapped[list["PropertyVersionModel"]] = relationship(back_populates="property", cascade="all, delete-orphan")
    property_type_ref: Mapped["PropertyTypeLookupModel"] = relationship(back_populates="properties")


class PropertyAddressModel(Base):
    __tablename__ = "property_addresses"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), unique=True
    )
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    province: Mapped[Optional[str]] = mapped_column(String(100))
    district: Mapped[Optional[str]] = mapped_column(String(100))
    neighborhood: Mapped[Optional[str]] = mapped_column(String(200))
    street: Mapped[Optional[str]] = mapped_column(String(300))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    address_line: Mapped[Optional[str]] = mapped_column(Text)
    address_line_2: Mapped[Optional[str]] = mapped_column(Text)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    elevation: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    geohash: Mapped[Optional[str]] = mapped_column(String(12))
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    property: Mapped[PropertyModel] = relationship(back_populates="address")


class PropertyBuildingModel(Base):
    __tablename__ = "property_buildings"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), unique=True
    )
    construction_year: Mapped[Optional[int]] = mapped_column(SmallInteger)
    building_age: Mapped[Optional[int]] = mapped_column(SmallInteger)
    floor_count: Mapped[Optional[int]] = mapped_column(SmallInteger)
    floor_number: Mapped[Optional[int]] = mapped_column(SmallInteger)
    unit_number: Mapped[Optional[str]] = mapped_column(String(50))
    net_area_sqm: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    gross_area_sqm: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    room_count: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1))
    living_room_count: Mapped[Optional[int]] = mapped_column(SmallInteger)
    bedroom_count: Mapped[Optional[int]] = mapped_column(SmallInteger)
    bathroom_count: Mapped[Optional[int]] = mapped_column(SmallInteger)
    balcony_count: Mapped[Optional[int]] = mapped_column(SmallInteger)
    parking_count: Mapped[Optional[int]] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    property: Mapped[PropertyModel] = relationship(back_populates="building")


class PropertyFeaturesModel(Base):
    __tablename__ = "property_features"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), unique=True
    )
    heating_type: Mapped[Optional[str]] = mapped_column(String(50))
    cooling_type: Mapped[Optional[str]] = mapped_column(String(50))
    energy_certificate_class: Mapped[Optional[str]] = mapped_column(String(1))
    has_elevator: Mapped[bool] = mapped_column(Boolean, default=False)
    has_parking: Mapped[bool] = mapped_column(Boolean, default=False)
    has_balcony: Mapped[bool] = mapped_column(Boolean, default=False)
    has_garden: Mapped[bool] = mapped_column(Boolean, default=False)
    has_pool: Mapped[bool] = mapped_column(Boolean, default=False)
    has_security: Mapped[bool] = mapped_column(Boolean, default=False)
    has_storage: Mapped[bool] = mapped_column(Boolean, default=False)
    has_smart_home: Mapped[bool] = mapped_column(Boolean, default=False)
    has_solar: Mapped[bool] = mapped_column(Boolean, default=False)
    has_ev_charger: Mapped[bool] = mapped_column(Boolean, default=False)
    accessibility_level: Mapped[Optional[str]] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    property: Mapped[PropertyModel] = relationship(back_populates="features")


class PropertyParcelModel(Base):
    __tablename__ = "property_parcels"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), unique=True
    )
    block: Mapped[Optional[str]] = mapped_column(String(50))
    parcel_number: Mapped[Optional[str]] = mapped_column(String(50))
    parcel_area_sqm: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    cadastral_reference: Mapped[Optional[str]] = mapped_column(String(100))
    zoning_type: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    property: Mapped[PropertyModel] = relationship(back_populates="parcel")


class PropertyImageModel(Base):
    __tablename__ = "property_images"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), index=True
    )
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1000))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(1000))
    caption: Mapped[Optional[str]] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    processing_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    property: Mapped[PropertyModel] = relationship(back_populates="images")


class PropertyVideoModel(Base):
    __tablename__ = "property_videos"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), index=True
    )
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1000))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(1000))
    caption: Mapped[Optional[str]] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    processing_status: Mapped[str] = mapped_column(String(20), default="pending")
    video_type: Mapped[Optional[str]] = mapped_column(String(30))
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    embed_url: Mapped[Optional[str]] = mapped_column(String(1000))
    provider: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    property: Mapped[PropertyModel] = relationship(back_populates="videos")


class PropertyDocumentModel(Base):
    __tablename__ = "property_documents"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), index=True
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1000))
    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    property: Mapped[PropertyModel] = relationship(back_populates="documents")


class PropertyAmenityModel(Base):
    __tablename__ = "property_amenities"
    __table_args__ = (
        UniqueConstraint("property_id", "amenity_code"),
        _TABLE_KWARGS,
    )
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE")
    )
    amenity_code: Mapped[str] = mapped_column(
        String(50),
        ForeignKey(fk_target("amenity_definitions", "code")),
        nullable=False,
    )
    value: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    property: Mapped[PropertyModel] = relationship(back_populates="amenities")
    amenity_definition: Mapped["AmenityDefinitionModel"] = relationship(back_populates="property_amenities")


class PropertyTagModel(Base):
    __tablename__ = "property_tags"
    __table_args__ = (UniqueConstraint("property_id", "tag"), _TABLE_KWARGS)
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE")
    )
    tag: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    property: Mapped[PropertyModel] = relationship(back_populates="tags")


class PropertyMetadataModel(Base):
    __tablename__ = "property_metadata"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), unique=True
    )
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    tenant_extensions: Mapped[dict] = mapped_column(JSONB, default=dict)
    schema_version: Mapped[str] = mapped_column(String(20), default="1.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    property: Mapped[PropertyModel] = relationship(back_populates="metadata_row")


class PropertyListingModel(Base):
    __tablename__ = "property_listings"
    __table_args__ = (
        UniqueConstraint("provider", "listing_id", name="uq_property_listings_provider_listing"),
        _TABLE_KWARGS,
    )
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), unique=True
    )
    original_url: Mapped[Optional[str]] = mapped_column(Text)
    provider: Mapped[Optional[str]] = mapped_column(String(50))
    listing_id: Mapped[Optional[str]] = mapped_column(String(100))
    listing_date: Mapped[Optional[date]] = mapped_column(Date)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sync_status: Mapped[str] = mapped_column(String(20), default="pending")
    provider_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    property: Mapped[PropertyModel] = relationship(back_populates="listing")


class PropertyOwnershipModel(Base):
    __tablename__ = "property_ownership"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), index=True
    )
    owner_type: Mapped[str] = mapped_column(String(30), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_external_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True))
    ownership_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    acquired_at: Mapped[Optional[date]] = mapped_column(Date)
    released_at: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    property: Mapped[PropertyModel] = relationship(back_populates="ownership")


class PropertyOwnershipHistoryModel(Base):
    __tablename__ = "property_ownership_history"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), index=True
    )
    owner_type: Mapped[str] = mapped_column(String(30), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_external_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True))
    ownership_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    acquired_at: Mapped[Optional[date]] = mapped_column(Date)
    released_at: Mapped[Optional[date]] = mapped_column(Date)
    effective_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    property: Mapped[PropertyModel] = relationship(back_populates="ownership_history")


class PropertyExternalSourceModel(Base):
    __tablename__ = "property_external_sources"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), index=True
    )
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_reference: Mapped[Optional[str]] = mapped_column(Text)
    source_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    imported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    property: Mapped[PropertyModel] = relationship(back_populates="external_sources")


class PropertyPriceHistoryModel(Base):
    __tablename__ = "property_price_history"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), index=True
    )
    price_type: Mapped[str] = mapped_column(String(20), nullable=False)
    old_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    new_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(3))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    changed_by: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True))
    change_reason: Mapped[Optional[str]] = mapped_column(String(200))
    property: Mapped[PropertyModel] = relationship(back_populates="price_history")


class PropertyStatusHistoryModel(Base):
    __tablename__ = "property_status_history"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), index=True
    )
    old_status: Mapped[str] = mapped_column(String(30), nullable=False)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    changed_by: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True))
    reason: Mapped[Optional[str]] = mapped_column(Text)
    property: Mapped[PropertyModel] = relationship(back_populates="status_history")


class PropertyVersionModel(Base):
    __tablename__ = "property_versions"
    __table_args__ = (
        UniqueConstraint("property_id", "version_number"),
        _TABLE_KWARGS,
    )
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True))
    property: Mapped[PropertyModel] = relationship(back_populates="versions")


class PropertyAuditLogModel(Base):
    __tablename__ = "property_audit_logs"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    property_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey(fk_target("properties"), ondelete="CASCADE"), index=True
    )
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(20), default="user")
    changes: Mapped[Optional[dict]] = mapped_column(JSONB)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    correlation_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    property: Mapped[PropertyModel] = relationship(back_populates="audit_logs")


class OutboxEventModel(Base):
    __tablename__ = "outbox_events"
    __table_args__ = _TABLE_KWARGS
    id: Mapped[UUID] = uuid_pk()
    aggregate_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    aggregate_type: Mapped[str] = mapped_column(String(50), default="Property")
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    metadata_json: Mapped[Optional[dict]] = mapped_column("metadata", JSONB)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    retry_count: Mapped[int] = mapped_column(SmallInteger, default=0)


class PropertyTypeLookupModel(Base):
    __tablename__ = "property_types"
    __table_args__ = _TABLE_KWARGS
    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    properties: Mapped[list[PropertyModel]] = relationship(back_populates="property_type_ref")


class AmenityDefinitionModel(Base):
    __tablename__ = "amenity_definitions"
    __table_args__ = _TABLE_KWARGS
    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[dict] = mapped_column(JSONB, nullable=False)
    value_type: Mapped[str] = mapped_column(String(20), default="boolean")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    property_amenities: Mapped[list[PropertyAmenityModel]] = relationship(back_populates="amenity_definition")
