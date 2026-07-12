from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCKER = ROOT / "docker"


class TestDockerStructure:
    def test_dockerignore_excludes_tests_and_docs(self) -> None:
        content = (ROOT / ".dockerignore").read_text()
        assert "tests/" in content
        assert "docs/" in content
        assert ".env" in content

    def test_init_db_sql(self) -> None:
        sql = (DOCKER / "init-db.sql").read_text()
        assert "postgis" in sql
        assert "CREATE SCHEMA IF NOT EXISTS property" in sql

    def test_api_dockerfile_multi_stage(self) -> None:
        dockerfile = (DOCKER / "Dockerfile").read_text()
        assert "AS builder" in dockerfile
        assert "AS runtime" in dockerfile
        assert "USER appuser" in dockerfile
        assert "HEALTHCHECK" in dockerfile
        assert '"--workers", "4"' in dockerfile

    def test_worker_dockerfile_has_libmagic(self) -> None:
        dockerfile = (DOCKER / "Dockerfile.worker").read_text()
        assert "libmagic1" in dockerfile
        assert "property.outbox" in dockerfile

    def test_compose_services(self) -> None:
        compose = (DOCKER / "docker-compose.yml").read_text()
        for service in (
            "api:",
            "worker:",
            "beat:",
            "postgres:",
            "redis:",
            "rabbitmq:",
            "minio:",
            "minio-init:",
        ):
            assert service in compose

    def test_compose_dev_reload_and_seed(self) -> None:
        compose = (DOCKER / "docker-compose.yml").read_text()
        assert "--reload" in compose
        assert "SEED_LOOKUPS: \"true\"" in compose
        assert "S3_ENDPOINT: http://minio:9000" in compose

    def test_compose_postgres_init_script(self) -> None:
        compose = (DOCKER / "docker-compose.yml").read_text()
        assert "init-db.sql:/docker-entrypoint-initdb.d/01-init.sql" in compose

    def test_prod_override(self) -> None:
        prod = (DOCKER / "docker-compose.prod.yml").read_text()
        assert 'RUN_MIGRATIONS: "false"' in prod
        assert "--workers 4" in prod
        assert "replicas: 2" in prod

    def test_entrypoint_supports_migrations_and_seed(self) -> None:
        entrypoint = (DOCKER / "entrypoint.sh").read_text()
        assert "RUN_MIGRATIONS" in entrypoint
        assert "SEED_LOOKUPS" in entrypoint
        assert "scripts.seed_property_types" in entrypoint

    def test_beat_uses_worker_image(self) -> None:
        compose = (DOCKER / "docker-compose.yml").read_text()
        assert "docker/Dockerfile.worker" in compose
        assert "beat" in compose
        assert "--schedule=/tmp/celerybeat-schedule" in compose

    def test_no_separate_beat_dockerfile(self) -> None:
        assert not (DOCKER / "Dockerfile.beat").exists()
