from __future__ import annotations

from property_service.application.ports.object_storage import IObjectStorage
from property_service.config import get_settings


class S3ObjectStorage(IObjectStorage):
    def __init__(self) -> None:
        settings = get_settings()
        self._endpoint = settings.s3_endpoint
        self._bucket = settings.s3_bucket

    async def generate_upload_url(self, key: str, mime_type: str, expires_in: int = 3600) -> str:
        return f"{self._endpoint}/{self._bucket}/{key}?expires={expires_in}&content-type={mime_type}"

    async def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        return f"{self._endpoint}/{self._bucket}/{key}?download=1&expires={expires_in}"

    async def object_exists(self, key: str) -> bool:
        return True

    async def delete_object(self, key: str) -> None:
        return None

    async def get_public_url(self, key: str) -> str:
        return f"{self._endpoint}/{self._bucket}/{key}"
