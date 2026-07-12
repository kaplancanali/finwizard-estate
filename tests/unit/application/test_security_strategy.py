from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from jose import jwt

from property_service.application.auth_context import AuthContext
from property_service.application.security.api_keys import ApiKeyRecord, register_dev_api_key
from property_service.application.security.authenticator import authenticate_request
from property_service.application.security.ownership import OwnershipGuard
from property_service.config.rbac import ROLE_PROPERTY_MANAGER, permissions_for_roles
from property_service.domain.aggregates.property import Property
from property_service.domain.entities.property_location import PropertyLocation
from property_service.domain.entities.property_version import PropertyExternalSource
from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.enums.source_type import SourceType
from property_service.domain.exceptions import AuthenticationError, AuthorizationError
from property_service.domain.services.listing_validator import ListingValidator
from property_service.domain.services.url_safety import assert_public_http_url
from property_service.domain.value_objects.geo_coordinate import GeoCoordinate
from property_service.domain.value_objects.property_classification import PropertyClassification
from property_service.domain.value_objects.property_code import PropertyCode
from property_service.domain.value_objects.slug import Slug
from property_service.presentation.schemas.search_schemas import GeoPolygonFilter
from decimal import Decimal
from starlette.requests import Request


def _request(headers: dict[str, str] | None = None) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/v1/properties",
        "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
        "client": ("127.0.0.1", 12345),
    }
    return Request(scope)


class TestRbacAndAuth:
    def test_dev_request_gets_property_manager_permissions(self, monkeypatch) -> None:
        monkeypatch.setenv("APP_ENV", "development")
        from property_service.config.settings import get_settings

        get_settings.cache_clear()
        auth = authenticate_request(_request())
        assert ROLE_PROPERTY_MANAGER in auth.roles
        assert "property:create" in auth.permissions

    def test_api_key_authentication(self) -> None:
        register_dev_api_key(
            ApiKeyRecord(
                key_id="pk_test_key",
                tenant_id=UUID("00000000-0000-0000-0000-000000000099"),
                permissions=frozenset({"property:read"}),
            )
        )
        auth = authenticate_request(_request({"X-API-Key": "pk_test_key"}))
        assert auth.actor_type == "api_key"
        assert auth.permissions == frozenset({"property:read"})

    def test_invalid_api_key_rejected(self) -> None:
        with pytest.raises(AuthenticationError):
            authenticate_request(_request({"X-API-Key": "invalid"}))


class TestOwnershipGuard:
    def _property(self, user_id: UUID) -> Property:
        return Property.create(
            tenant_id=UUID("00000000-0000-0000-0000-000000000010"),
            property_code=PropertyCode("FW-TR-IST-00000100"),
            slug=Slug("ownership-test"),
            title="Ownership",
            classification=PropertyClassification(PropertyType.APARTMENT, PropertyCategory.RESIDENTIAL),
            location=PropertyLocation(country_code="TR", province="Istanbul"),
            created_by=user_id,
            source=PropertyExternalSource(source_type=SourceType.MANUAL),
        )

    def test_creator_can_modify(self) -> None:
        user_id = uuid4()
        auth = AuthContext(
            user_id=user_id,
            tenant_id=UUID("00000000-0000-0000-0000-000000000010"),
            permissions=permissions_for_roles(frozenset()),
        )
        assert OwnershipGuard.can_modify_property(auth, self._property(user_id)) is False

        auth_mgr = AuthContext(
            user_id=uuid4(),
            tenant_id=UUID("00000000-0000-0000-0000-000000000010"),
            roles=frozenset({ROLE_PROPERTY_MANAGER}),
            permissions=permissions_for_roles(frozenset({ROLE_PROPERTY_MANAGER})),
        )
        assert OwnershipGuard.can_modify_property(auth_mgr, self._property(user_id)) is True

    def test_unauthorized_modifier_raises(self) -> None:
        owner_id = uuid4()
        auth = AuthContext(
            user_id=uuid4(),
            tenant_id=UUID("00000000-0000-0000-0000-000000000010"),
            permissions=frozenset({"property:update"}),
        )
        with pytest.raises(AuthorizationError):
            OwnershipGuard.assert_can_modify(auth, self._property(owner_id))


class TestInputSecurity:
    def test_localhost_listing_url_blocked(self) -> None:
        with pytest.raises(Exception):
            ListingValidator.validate_url("http://localhost/listing/1")

    def test_polygon_point_limit(self) -> None:
        with pytest.raises(Exception):
            GeoPolygonFilter(
                coordinates=[[Decimal("41.0"), Decimal("29.0")] for _ in range(1001)],
            )
