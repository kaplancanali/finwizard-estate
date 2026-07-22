.PHONY: install test lint run up down build migrate docker-up docker-down docker-logs helm-template seed-demo

COMPOSE = docker compose -f docker/docker-compose.yml
COMPOSE_PROD = docker compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml

install:
	pip3 install -e ".[dev]"

test:
	python3 -m pytest tests/ -v

lint:
	ruff check src/ tests/

run:
	uvicorn property_service.main:app --reload --host 0.0.0.0 --port 8000

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

migrate:
	$(COMPOSE) exec api alembic upgrade head

seed-demo:
	PROPERTY_API_BASE=http://localhost:8001/api/v1 python3 scripts/seed_demo_properties.py

docker-up:
	$(COMPOSE) up -d --build

docker-down:
	$(COMPOSE) down

docker-logs:
	$(COMPOSE) logs -f api worker

logs: docker-logs

docker-test:
	$(COMPOSE) exec api pytest

prod-up:
	$(COMPOSE_PROD) up -d --build

roadmap-status:
	python3 scripts/roadmap_status.py

helm-template:
	helm template property-service deploy/helm/property-service \
		-f deploy/helm/property-service/values-dev.yaml \
		--set secrets.databaseUrl=postgresql+asyncpg://u:p@host/db \
		--set secrets.redisUrl=redis://redis:6379/0 \
		--set secrets.rabbitmqUrl=amqp://u:p@rabbitmq/ \
		--set secrets.jwtSecret=dev-secret
