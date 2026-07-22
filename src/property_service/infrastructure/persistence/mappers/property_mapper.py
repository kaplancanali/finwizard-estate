from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from property_service.domain.aggregates.property import Property
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
from property_service.domain.enums.document_type import DocumentType
from property_service.domain.enums.listing_provider import ListingProvider
from property_service.domain.enums.owner_type import OwnerType
from property_service.domain.enums.processing_status import ProcessingStatus
from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.enums.property_visibility import PropertyVisibility
from property_service.domain.enums.source_type import SourceType
from property_service.domain.enums.sync_status import SyncStatus
from property_service.domain.value_objects.geo_coordinate import GeoCoordinate
from property_service.domain.value_objects.property_classification import PropertyClassification
from property_service.domain.value_objects.property_code import PropertyCode
from property_service.domain.value_objects.slug import Slug
from property_service.infrastructure.persistence.models import (
    PropertyAddressModel,
    PropertyAmenityModel,
    PropertyAuditLogModel,
    PropertyBuildingModel,
    PropertyDocumentModel,
    PropertyExternalSourceModel,
    PropertyFeaturesModel,
    PropertyImageModel,
    PropertyListingModel,
    PropertyMetadataModel,
    PropertyModel,
    PropertyOwnershipModel,
    PropertyParcelModel,
    PropertyPriceHistoryModel,
    PropertyStatusHistoryModel,
    PropertyTagModel,
    PropertyVideoModel,
    PropertyOwnershipHistoryModel,
)


class PropertyMapper:
    @staticmethod
    def to_domain(model: PropertyModel) -> Property:
        coordinate = None
        lat = model.latitude
        lng = model.longitude
        if model.address and model.address.latitude is not None:
            lat = model.address.latitude
            lng = model.address.longitude
        if lat is not None and lng is not None:
            elevation = model.address.elevation if model.address else None
            coordinate = GeoCoordinate(lat, lng, elevation)

        location = PropertyLocation(
            country_code=model.country_code,
            province=model.province,
            district=model.district,
            neighborhood=model.neighborhood,
            street=model.address.street if model.address else None,
            postal_code=model.address.postal_code if model.address else None,
            address_line=model.address.address_line if model.address else None,
            address_line_2=model.address.address_line_2 if model.address else None,
            coordinate=coordinate,
            geohash=model.geohash,
            timezone=model.address.timezone if model.address else None,
            is_verified=model.address.is_verified if model.address else False,
        )

        building = None
        if model.building:
            b = model.building
            building = PropertyBuilding(
                construction_year=b.construction_year,
                building_age=b.building_age,
                floor_count=b.floor_count,
                floor_number=b.floor_number,
                unit_number=b.unit_number,
                net_area_sqm=b.net_area_sqm,
                gross_area_sqm=b.gross_area_sqm,
                room_count=b.room_count,
                living_room_count=b.living_room_count,
                bedroom_count=b.bedroom_count,
                bathroom_count=b.bathroom_count,
                balcony_count=b.balcony_count,
                parking_count=b.parking_count,
            )

        features = PropertyFeatures()
        if model.features:
            f = model.features
            features = PropertyFeatures(
                heating_type=f.heating_type,
                cooling_type=f.cooling_type,
                energy_certificate_class=f.energy_certificate_class,
                has_elevator=f.has_elevator,
                has_parking=f.has_parking,
                has_balcony=f.has_balcony,
                has_garden=f.has_garden,
                has_pool=f.has_pool,
                has_security=f.has_security,
                has_storage=f.has_storage,
                has_smart_home=f.has_smart_home,
                has_solar=f.has_solar,
                has_ev_charger=f.has_ev_charger,
                accessibility_level=f.accessibility_level,
            )

        parcel = None
        if model.parcel:
            p = model.parcel
            parcel = PropertyParcel(
                block=p.block,
                parcel_number=p.parcel_number,
                parcel_area_sqm=p.parcel_area_sqm,
                cadastral_reference=p.cadastral_reference,
                zoning_type=p.zoning_type,
            )

        listing = None
        if model.listing:
            l = model.listing
            listing = PropertyListing(
                original_url=l.original_url,
                provider=ListingProvider(l.provider) if l.provider else None,
                listing_id=l.listing_id,
                listing_date=l.listing_date,
                last_synced_at=l.last_synced_at,
                sync_status=SyncStatus(l.sync_status),
                provider_metadata=l.provider_metadata,
            )

        metadata = PropertyMetadata()
        if model.metadata_row:
            metadata = PropertyMetadata(
                metadata=model.metadata_row.metadata_json or {},
                tenant_extensions=model.metadata_row.tenant_extensions or {},
                schema_version=model.metadata_row.schema_version,
            )

        return Property(
            id=model.id,
            tenant_id=model.tenant_id,
            property_code=PropertyCode(model.property_code),
            slug=Slug(model.slug),
            title=model.title,
            classification=PropertyClassification(
                property_type=PropertyType(model.property_type),
                category=PropertyCategory(model.property_category),
                subtype=model.property_subtype,
            ),
            location=location,
            created_by=model.created_by,
            status=PropertyStatus(model.status),
            visibility=PropertyVisibility(model.visibility),
            description=model.description,
            summary=model.summary,
            pricing=PropertyPricing(
                sale_price=model.sale_price,
                rental_price=model.rental_price,
                maintenance_fee=model.maintenance_fee,
                currency=model.currency,
                price_on_request=model.price_on_request,
                price_per_sqm=model.price_per_sqm,
            ),
            parcel=parcel,
            building=building,
            features=features,
            amenities=[
                PropertyAmenity(amenity_code=a.amenity_code, value=a.value, id=a.id)
                for a in model.amenities
            ],
            images=[
                PropertyImage(
                    id=i.id,
                    storage_key=i.storage_key,
                    url=i.url,
                    thumbnail_url=i.thumbnail_url,
                    caption=i.caption,
                    sort_order=i.sort_order,
                    is_primary=i.is_primary,
                    width=i.width,
                    height=i.height,
                    file_size=i.file_size,
                    mime_type=i.mime_type,
                    processing_status=ProcessingStatus(i.processing_status),
                    deleted_at=i.deleted_at,
                )
                for i in model.images
            ],
            videos=[
                PropertyVideo(
                    id=v.id,
                    storage_key=v.storage_key,
                    url=v.url,
                    thumbnail_url=v.thumbnail_url,
                    caption=v.caption,
                    sort_order=v.sort_order,
                    is_primary=v.is_primary,
                    mime_type=v.mime_type,
                    file_size=v.file_size,
                    processing_status=ProcessingStatus(v.processing_status),
                    video_type=v.video_type or "standard",
                    embed_url=v.embed_url,
                    provider=v.provider,
                    duration_seconds=v.duration_seconds,
                    deleted_at=v.deleted_at,
                )
                for v in model.videos
            ],
            documents=[
                PropertyDocument(
                    id=d.id,
                    document_type=DocumentType(d.document_type),
                    storage_key=d.storage_key,
                    url=d.url,
                    file_name=d.file_name,
                    mime_type=d.mime_type,
                    file_size=d.file_size,
                    verified=d.verified,
                    verified_at=d.verified_at,
                    verified_by=d.verified_by,
                    deleted_at=d.deleted_at,
                )
                for d in model.documents
            ],
            listing=listing,
            ownership=[
                PropertyOwnership(
                    id=o.id,
                    owner_type=OwnerType(o.owner_type),
                    owner_name=o.owner_name,
                    owner_external_id=o.owner_external_id,
                    ownership_percentage=o.ownership_percentage,
                    acquired_at=o.acquired_at,
                    released_at=o.released_at,
                    is_current=o.is_current,
                )
                for o in model.ownership
            ],
            ownership_history=[
                OwnershipHistoryEntry(
                    id=h.id,
                    owner_type=OwnerType(h.owner_type),
                    owner_name=h.owner_name,
                    owner_external_id=h.owner_external_id,
                    ownership_percentage=h.ownership_percentage,
                    acquired_at=h.acquired_at,
                    released_at=h.released_at,
                    effective_from=h.effective_from,
                    effective_to=h.effective_to,
                )
                for h in model.ownership_history
            ],
            tags=[t.tag for t in model.tags],
            metadata=metadata,
            external_sources=[
                PropertyExternalSource(
                    id=s.id,
                    source_type=SourceType(s.source_type),
                    source_reference=s.source_reference,
                    source_payload=s.source_payload,
                    imported_at=s.imported_at,
                )
                for s in model.external_sources
            ],
            price_history=[
                PriceHistoryEntry(
                    id=h.id,
                    price_type=h.price_type,
                    old_amount=h.old_amount,
                    new_amount=h.new_amount,
                    currency=h.currency,
                    changed_by=h.changed_by,
                    change_reason=h.change_reason,
                )
                for h in model.price_history
            ],
            status_history=[
                StatusHistoryEntry(
                    id=h.id,
                    old_status=h.old_status,
                    new_status=h.new_status,
                    changed_by=h.changed_by,
                    reason=h.reason,
                )
                for h in model.status_history
            ],
            audit_logs=[
                PropertyAuditLog(
                    id=a.id,
                    action=a.action,
                    actor_id=a.actor_id,
                    actor_type=a.actor_type,
                    changes=a.changes,
                    ip_address=a.ip_address,
                    correlation_id=a.correlation_id,
                )
                for a in model.audit_logs
            ],
            version=model.version,
            published_at=model.published_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            updated_by=model.updated_by,
        )

    @staticmethod
    def apply_to_model(domain: Property, model: PropertyModel) -> PropertyModel:
        model.tenant_id = domain.tenant_id
        model.property_code = str(domain.property_code)
        model.slug = str(domain.slug)
        model.title = domain.title
        model.description = domain.description
        model.summary = domain.summary
        model.property_type = domain.classification.property_type.value
        model.property_category = domain.classification.category.value
        model.property_subtype = domain.classification.subtype
        model.status = domain.status.value
        model.visibility = domain.visibility.value
        model.sale_price = domain.pricing.sale_price
        model.rental_price = domain.pricing.rental_price
        model.maintenance_fee = domain.pricing.maintenance_fee
        model.currency = domain.pricing.currency
        model.price_on_request = domain.pricing.price_on_request
        model.price_per_sqm = domain.pricing.price_per_sqm
        model.country_code = domain.location.country_code
        model.province = domain.location.province
        model.district = domain.location.district
        model.neighborhood = domain.location.neighborhood
        model.latitude = domain.location.latitude
        model.longitude = domain.location.longitude
        model.geohash = domain.location.geohash
        model.net_area_sqm = domain.building.net_area_sqm if domain.building else None
        model.gross_area_sqm = domain.building.gross_area_sqm if domain.building else None
        model.room_count = domain.building.room_count if domain.building else None
        model.bathroom_count = domain.building.bathroom_count if domain.building else None
        model.construction_year = domain.building.construction_year if domain.building else None
        model.floor_number = domain.building.floor_number if domain.building else None
        model.parking_count = domain.building.parking_count if domain.building else None
        model.has_elevator = domain.features.has_elevator
        model.heating_type = domain.features.heating_type
        model.version = domain.version
        model.published_at = domain.published_at
        model.updated_at = domain.updated_at
        model.deleted_at = domain.deleted_at
        model.updated_by = domain.updated_by

        PropertyMapper._sync_address(domain, model)
        PropertyMapper._sync_building(domain, model)
        PropertyMapper._sync_features(domain, model)
        PropertyMapper._sync_parcel(domain, model)
        PropertyMapper._sync_metadata(domain, model)
        PropertyMapper._sync_listing(domain, model)
        PropertyMapper._sync_amenities(domain, model)
        PropertyMapper._sync_tags(domain, model)
        PropertyMapper._sync_images(domain, model)
        PropertyMapper._sync_videos(domain, model)
        PropertyMapper._sync_documents(domain, model)
        PropertyMapper._sync_ownership(domain, model)
        PropertyMapper._sync_ownership_history(domain, model)
        PropertyMapper._sync_external_sources(domain, model)
        PropertyMapper._sync_price_history(domain, model)
        PropertyMapper._sync_status_history(domain, model)
        return model

    @staticmethod
    def to_model(domain: Property) -> PropertyModel:
        model = PropertyModel(
            id=domain.id,
            tenant_id=domain.tenant_id,
            property_code=str(domain.property_code),
            slug=str(domain.slug),
            title=domain.title,
            created_by=domain.created_by,
            created_at=domain.created_at,
        )
        return PropertyMapper.apply_to_model(domain, model)

    @staticmethod
    def _sync_address(domain: Property, model: PropertyModel) -> None:
        loc = domain.location
        if model.address is None:
            model.address = PropertyAddressModel(property_id=model.id)
        addr = model.address
        addr.country_code = loc.country_code
        addr.province = loc.province
        addr.district = loc.district
        addr.neighborhood = loc.neighborhood
        addr.street = loc.street
        addr.postal_code = loc.postal_code
        addr.address_line = loc.address_line
        addr.address_line_2 = loc.address_line_2
        addr.latitude = loc.latitude
        addr.longitude = loc.longitude
        addr.elevation = loc.elevation
        addr.geohash = loc.geohash
        addr.timezone = loc.timezone
        addr.is_verified = loc.is_verified

    @staticmethod
    def _sync_building(domain: Property, model: PropertyModel) -> None:
        if domain.building is None:
            model.building = None
            return
        if model.building is None:
            model.building = PropertyBuildingModel(property_id=model.id)
        b = domain.building
        m = model.building
        m.construction_year = b.construction_year
        m.building_age = b.building_age
        m.floor_count = b.floor_count
        m.floor_number = b.floor_number
        m.unit_number = b.unit_number
        m.net_area_sqm = b.net_area_sqm
        m.gross_area_sqm = b.gross_area_sqm
        m.room_count = b.room_count
        m.living_room_count = b.living_room_count
        m.bedroom_count = b.bedroom_count
        m.bathroom_count = b.bathroom_count
        m.balcony_count = b.balcony_count
        m.parking_count = b.parking_count

    @staticmethod
    def _sync_features(domain: Property, model: PropertyModel) -> None:
        if model.features is None:
            model.features = PropertyFeaturesModel(property_id=model.id)
        f = domain.features
        m = model.features
        m.heating_type = f.heating_type
        m.cooling_type = f.cooling_type
        m.energy_certificate_class = f.energy_certificate_class
        m.has_elevator = f.has_elevator
        m.has_parking = f.has_parking
        m.has_balcony = f.has_balcony
        m.has_garden = f.has_garden
        m.has_pool = f.has_pool
        m.has_security = f.has_security
        m.has_storage = f.has_storage
        m.has_smart_home = f.has_smart_home
        m.has_solar = f.has_solar
        m.has_ev_charger = f.has_ev_charger
        m.accessibility_level = f.accessibility_level

    @staticmethod
    def _sync_parcel(domain: Property, model: PropertyModel) -> None:
        if domain.parcel is None:
            return
        if model.parcel is None:
            model.parcel = PropertyParcelModel(property_id=model.id)
        model.parcel.block = domain.parcel.block
        model.parcel.parcel_number = domain.parcel.parcel_number
        model.parcel.parcel_area_sqm = domain.parcel.parcel_area_sqm
        model.parcel.cadastral_reference = domain.parcel.cadastral_reference
        model.parcel.zoning_type = domain.parcel.zoning_type

    @staticmethod
    def _sync_metadata(domain: Property, model: PropertyModel) -> None:
        if model.metadata_row is None:
            model.metadata_row = PropertyMetadataModel(property_id=model.id)
        model.metadata_row.metadata_json = domain.metadata.metadata
        model.metadata_row.tenant_extensions = domain.metadata.tenant_extensions
        model.metadata_row.schema_version = domain.metadata.schema_version

    @staticmethod
    def _sync_listing(domain: Property, model: PropertyModel) -> None:
        if domain.listing is None:
            return
        if model.listing is None:
            model.listing = PropertyListingModel(property_id=model.id)
        l = domain.listing
        m = model.listing
        m.original_url = l.original_url
        m.provider = l.provider.value if l.provider else None
        m.listing_id = l.listing_id
        m.listing_date = l.listing_date
        m.last_synced_at = l.last_synced_at
        m.sync_status = l.sync_status.value
        m.provider_metadata = l.provider_metadata

    @staticmethod
    def _sync_tags(domain: Property, model: PropertyModel) -> None:
        desired = list(dict.fromkeys(domain.tags))
        existing = {row.tag: row for row in list(model.tags)}
        for tag, row in existing.items():
            if tag not in desired:
                model.tags.remove(row)
        for tag in desired:
            if tag not in existing:
                model.tags.append(PropertyTagModel(property_id=model.id, tag=tag))

    @staticmethod
    def _sync_amenities(domain: Property, model: PropertyModel) -> None:
        desired_codes = {a.amenity_code: a for a in domain.amenities}
        existing = {row.amenity_code: row for row in list(model.amenities)}
        for code, row in existing.items():
            if code not in desired_codes:
                model.amenities.remove(row)
            else:
                row.value = desired_codes[code].value
        for code, amenity in desired_codes.items():
            if code not in existing:
                model.amenities.append(
                    PropertyAmenityModel(
                        property_id=model.id,
                        amenity_code=amenity.amenity_code,
                        value=amenity.value,
                        id=amenity.id,
                    )
                )

    @staticmethod
    def _sync_images(domain: Property, model: PropertyModel) -> None:
        model.images = [
            PropertyImageModel(
                id=i.id,
                property_id=model.id,
                storage_key=i.storage_key,
                url=i.url,
                thumbnail_url=i.thumbnail_url,
                caption=i.caption,
                sort_order=i.sort_order,
                is_primary=i.is_primary,
                width=i.width,
                height=i.height,
                file_size=i.file_size,
                mime_type=i.mime_type,
                processing_status=i.processing_status.value,
                deleted_at=i.deleted_at,
            )
            for i in domain.images
        ]

    @staticmethod
    def _sync_videos(domain: Property, model: PropertyModel) -> None:
        model.videos = [
            PropertyVideoModel(
                id=v.id,
                property_id=model.id,
                storage_key=v.storage_key,
                url=v.url,
                thumbnail_url=v.thumbnail_url,
                caption=v.caption,
                sort_order=v.sort_order,
                is_primary=v.is_primary,
                mime_type=v.mime_type,
                file_size=v.file_size,
                processing_status=v.processing_status.value,
                video_type=v.video_type,
                embed_url=v.embed_url,
                provider=v.provider,
                duration_seconds=v.duration_seconds,
                deleted_at=v.deleted_at,
            )
            for v in domain.videos
        ]

    @staticmethod
    def _sync_documents(domain: Property, model: PropertyModel) -> None:
        model.documents = [
            PropertyDocumentModel(
                id=d.id,
                property_id=model.id,
                document_type=d.document_type.value,
                storage_key=d.storage_key,
                url=d.url,
                file_name=d.file_name,
                mime_type=d.mime_type,
                file_size=d.file_size,
                verified=d.verified,
                verified_at=d.verified_at,
                verified_by=d.verified_by,
                deleted_at=d.deleted_at,
            )
            for d in domain.documents
        ]

    @staticmethod
    def _sync_ownership(domain: Property, model: PropertyModel) -> None:
        model.ownership = [
            PropertyOwnershipModel(
                id=o.id,
                property_id=model.id,
                owner_type=o.owner_type.value,
                owner_name=o.owner_name,
                owner_external_id=o.owner_external_id,
                ownership_percentage=o.ownership_percentage,
                acquired_at=o.acquired_at,
                released_at=o.released_at,
                is_current=o.is_current,
            )
            for o in domain.ownership
        ]

    @staticmethod
    def _sync_ownership_history(domain: Property, model: PropertyModel) -> None:
        existing_ids = {h.id for h in model.ownership_history}
        for h in domain.ownership_history:
            if h.id not in existing_ids:
                model.ownership_history.append(
                    PropertyOwnershipHistoryModel(
                        id=h.id,
                        property_id=model.id,
                        owner_type=h.owner_type.value,
                        owner_name=h.owner_name,
                        owner_external_id=h.owner_external_id,
                        ownership_percentage=h.ownership_percentage,
                        acquired_at=h.acquired_at,
                        released_at=h.released_at,
                        effective_from=h.effective_from,
                        effective_to=h.effective_to,
                    )
                )

    @staticmethod
    def _sync_external_sources(domain: Property, model: PropertyModel) -> None:
        model.external_sources = [
            PropertyExternalSourceModel(
                id=s.id,
                property_id=model.id,
                source_type=s.source_type.value,
                source_reference=s.source_reference,
                source_payload=s.source_payload,
                imported_at=s.imported_at,
            )
            for s in domain.external_sources
        ]

    @staticmethod
    def _sync_price_history(domain: Property, model: PropertyModel) -> None:
        existing_ids = {h.id for h in model.price_history}
        for h in domain.price_history:
            if h.id not in existing_ids:
                model.price_history.append(
                    PropertyPriceHistoryModel(
                        id=h.id,
                        property_id=model.id,
                        price_type=h.price_type,
                        old_amount=h.old_amount,
                        new_amount=h.new_amount,
                        currency=h.currency,
                        changed_by=h.changed_by,
                        change_reason=h.change_reason,
                    )
                )

    @staticmethod
    def _sync_status_history(domain: Property, model: PropertyModel) -> None:
        existing_ids = {h.id for h in model.status_history}
        for h in domain.status_history:
            if h.id not in existing_ids:
                model.status_history.append(
                    PropertyStatusHistoryModel(
                        id=h.id,
                        property_id=model.id,
                        old_status=h.old_status,
                        new_status=h.new_status,
                        changed_by=h.changed_by,
                        reason=h.reason,
                    )
                )
