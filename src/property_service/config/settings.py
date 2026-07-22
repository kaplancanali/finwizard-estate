from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "property-service"
    app_env: str = "development"
    log_level: str = "INFO"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://property:property@localhost:5432/property_db"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://property:property@localhost:5672/"

    s3_endpoint: str | None = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "property-media"
    s3_region: str = "us-east-1"

    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_audience: str = "property-service"
    jwt_issuer: str | None = None
    jwks_url: str | None = None
    require_authentication: bool = False

    # External platform APIs (filled from Identity / finward-api when available)
    identity_base_url: str | None = None
    finward_api_base_url: str | None = None
    nominatim_url: str = "https://nominatim.openstreetmap.org"

    redis_max_connections: int = 20
    use_in_memory_cache: bool = False

    rate_limit_per_minute: int = 600
    rate_limit_unauthenticated_per_minute: int = 60
    presigned_url_ttl_seconds: int = 3600

    run_migrations: bool = False
    seed_lookups: bool = False

    cors_origins: list[str] = ["*"]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def cache_backend(self) -> str:
        if self.use_in_memory_cache or self.is_development:
            return "memory"
        return "redis"


@lru_cache
def get_settings() -> Settings:
    return Settings()
