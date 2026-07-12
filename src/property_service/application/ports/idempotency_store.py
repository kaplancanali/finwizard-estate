from __future__ import annotations

from abc import ABC, abstractmethod


class IIdempotencyStore(ABC):
    @abstractmethod
    async def get_response(self, key: str) -> dict | None: ...

    @abstractmethod
    async def store_response(
        self,
        key: str,
        response: dict,
        ttl: int = 86400,
    ) -> None: ...

    @abstractmethod
    async def is_processing(self, key: str) -> bool: ...

    @abstractmethod
    async def mark_processing(self, key: str, ttl: int = 300) -> bool:
        """Returns False if already processing (SET NX)."""
        ...
