from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ListingAdapter(ABC):
    @abstractmethod
    async def fetch_listing(self, url: str) -> dict[str, Any]: ...

    @abstractmethod
    def supports_url(self, url: str) -> bool: ...
