from __future__ import annotations

import inspect

import pytest

from property_service.application.dto.property_create_dto import CreatePropertyDTO
from property_service.application.dto.property_search_dto import PropertySearchCriteria, SearchFilterSet
from property_service.application.mappers.domain_mappers import create_property_data_from_dto
from property_service.presentation.mappers.request_mappers import create_property_dto_from_request
from property_service.presentation.schemas.bulk_schemas import BulkImportRequest, BulkImportOptions
from property_service.presentation.schemas.media_schemas import ImageUploadRequest
from property_service.presentation.schemas.property_schemas import LocationInput, PropertyCreateRequest
from property_service.presentation.schemas.search_schemas import PropertySearchRequest, SearchFilters
from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_type import PropertyType


class TestDtoDesign:
    def test_create_property_dto_flow(self) -> None:
        request = PropertyCreateRequest(
            title="Modern Apartment",
            property_type=PropertyType.APARTMENT,
            property_category=PropertyCategory.RESIDENTIAL,
            location=LocationInput(
                country_code="TR",
                province="Istanbul",
                district="Kadikoy",
                latitude="40.9876",
                longitude="29.0234",
            ),
        )
        dto = create_property_dto_from_request(request, tenant_id=__import__("uuid").uuid4(), user_id=__import__("uuid").uuid4())
        assert isinstance(dto, CreatePropertyDTO)
        data = create_property_data_from_dto(dto)
        assert data.title == "Modern Apartment"

    def test_location_validator_requires_address_or_coords(self) -> None:
        with pytest.raises(ValueError):
            LocationInput(country_code="TR")

    def test_property_search_request_typed_filters(self) -> None:
        body = PropertySearchRequest(
            query="apartment",
            filters=SearchFilters(provinces=["Istanbul"]),
        )
        assert body.filters.provinces == ["Istanbul"]

    def test_bulk_import_request_shape(self) -> None:
        request = BulkImportRequest(
            source_type="manual",
            items=[
                PropertyCreateRequest(
                    title="Import Item",
                    property_type=PropertyType.APARTMENT,
                    property_category=PropertyCategory.RESIDENTIAL,
                    location=LocationInput(
                        country_code="TR",
                        province="Istanbul",
                        district="Kadikoy",
                        latitude="40.9876",
                        longitude="29.0234",
                    ),
                )
            ],
            options=BulkImportOptions(),
        )
        assert request.options.skip_duplicates is True
        assert len(request.items) == 1

    def test_image_upload_validation_pattern(self) -> None:
        req = ImageUploadRequest(
            file_name="photo.jpg",
            mime_type="image/jpeg",
            file_size=1024,
        )
        assert req.mime_type == "image/jpeg"

    def test_mapper_modules_exist(self) -> None:
        from property_service.presentation.mappers import request_mappers, response_mappers
        from property_service.application.mappers import domain_mappers
        from property_service.infrastructure.persistence.mappers import search_mapper

        assert inspect.ismodule(request_mappers)
        assert inspect.ismodule(response_mappers)
        assert inspect.ismodule(domain_mappers)
        assert hasattr(search_mapper, "SearchMapper")

    def test_application_search_criteria_helpers(self) -> None:
        criteria = PropertySearchCriteria(filters=SearchFilterSet(raw={"status": ["draft"]}))
        assert criteria.filters_dict["status"] == ["draft"]
