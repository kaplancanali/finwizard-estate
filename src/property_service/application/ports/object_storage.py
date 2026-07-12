from __future__ import annotations

from abc import ABC, abstractmethod


class IObjectStorage(ABC):
    @abstractmethod
    async def generate_upload_url(
        self,
        key: str,
        mime_type: str,
        expires_in: int = 3600,
    ) -> str: ...

    @abstractmethod
    async def generate_download_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str: ...

    @abstractmethod
    async def object_exists(self, key: str) -> bool: ...

    @abstractmethod
    async def delete_object(self, key: str) -> None: ...
