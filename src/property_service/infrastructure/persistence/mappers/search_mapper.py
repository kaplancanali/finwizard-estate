from __future__ import annotations

from property_service.application.dto.property_search_dto import PropertySummary
from property_service.infrastructure.persistence.models import PropertyModel


class SearchMapper:
    @staticmethod
    def to_summary(model: PropertyModel) -> PropertySummary:
        primary_url = None
        images = getattr(model, "images", None) or []
        active = [img for img in images if getattr(img, "deleted_at", None) is None]
        if active:
            primary = next((img for img in active if img.is_primary), active[0])
            primary_url = primary.url or primary.thumbnail_url

        return PropertySummary(
            id=model.id,
            property_code=model.property_code,
            slug=model.slug,
            title=model.title,
            property_type=model.property_type,
            status=model.status,
            sale_price=model.sale_price,
            rental_price=model.rental_price,
            currency=model.currency,
            province=model.province,
            district=model.district,
            neighborhood=model.neighborhood,
            latitude=model.latitude,
            longitude=model.longitude,
            net_area_sqm=model.net_area_sqm,
            room_count=model.room_count,
            bathroom_count=model.bathroom_count,
            primary_image_url=primary_url,
            created_at=model.created_at,
        )
