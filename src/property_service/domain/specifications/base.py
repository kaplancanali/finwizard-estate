from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from property_service.domain.aggregates.property import Property


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate: Property) -> bool:
        ...

    @abstractmethod
    def to_filter(self) -> dict[str, Any]:
        """Convert to repository/search filter criteria."""
        ...


class AndSpecification(Specification):
    def __init__(self, *specs: Specification) -> None:
        self._specs = specs

    def is_satisfied_by(self, candidate: Property) -> bool:
        return all(s.is_satisfied_by(candidate) for s in self._specs)

    def to_filter(self) -> dict[str, Any]:
        return {"and": [s.to_filter() for s in self._specs]}


class TenantPropertySpec(Specification):
    def __init__(self, tenant_id: UUID) -> None:
        self.tenant_id = tenant_id

    def is_satisfied_by(self, candidate: Property) -> bool:
        return candidate.tenant_id == self.tenant_id

    def to_filter(self) -> dict[str, Any]:
        return {"tenant_id": str(self.tenant_id)}


class ActivePropertySpec(Specification):
    def is_satisfied_by(self, candidate: Property) -> bool:
        from property_service.domain.enums.property_status import PropertyStatus
        return (
            candidate.deleted_at is None
            and candidate.status in (PropertyStatus.ACTIVE, PropertyStatus.LISTED)
        )

    def to_filter(self) -> dict[str, Any]:
        return {"status": ["active", "listed"], "deleted_at": None}


class PriceRangeSpec(Specification):
    def __init__(self, min_price: float | None = None, max_price: float | None = None) -> None:
        self.min_price = min_price
        self.max_price = max_price

    def is_satisfied_by(self, candidate: Property) -> bool:
        price = candidate.pricing.sale_price
        if price is None:
            return False
        if self.min_price is not None and price < self.min_price:
            return False
        return not (self.max_price is not None and price > self.max_price)

    def to_filter(self) -> dict[str, Any]:
        return {"sale_price": {"min": self.min_price, "max": self.max_price}}
