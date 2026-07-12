# 2. Folder Structure

Clean Architecture + DDD layered structure. Dependencies flow **inward only**.

```
property-service/
├── pyproject.toml
├── README.md
├── alembic.ini
├── .env.example
├── Makefile
│
├── docker/
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── entrypoint.sh
│
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
│
├── scripts/
│   ├── seed_property_types.py
│   └── generate_openapi.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/
│   │   ├── repositories/
│   │   ├── api/
│   │   └── events/
│   └── performance/
│       └── test_search_benchmark.py
│
└── src/
    └── property_service/
        ├── __init__.py
        ├── main.py                          # FastAPI app factory
        │
        ├── config/
        │   ├── __init__.py
        │   ├── settings.py                  # Pydantic Settings
        │   └── logging.py
        │
        ├── domain/                          # ★ INNERMOST — zero infra deps
        │   ├── __init__.py
        │   ├── aggregates/
        │   │   ├── __init__.py
        │   │   └── property.py              # Property aggregate root
        │   ├── entities/
        │   │   ├── property_pricing.py
        │   │   ├── property_location.py
        │   │   ├── property_building.py
        │   │   ├── property_parcel.py
        │   │   ├── property_image.py
        │   │   ├── property_document.py
        │   │   ├── property_listing.py
        │   │   ├── property_ownership.py
        │   │   └── property_version.py
        │   ├── value_objects/
        │   │   ├── property_code.py
        │   │   ├── slug.py
        │   │   ├── geo_coordinate.py
        │   │   ├── money.py
        │   │   └── area.py
        │   ├── enums/
        │   │   ├── property_type.py
        │   │   ├── property_status.py
        │   │   ├── property_category.py
        │   │   ├── source_type.py
        │   │   └── document_type.py
        │   ├── events/
        │   │   ├── base.py
        │   │   ├── property_created.py
        │   │   ├── property_updated.py
        │   │   ├── property_deleted.py
        │   │   ├── property_price_changed.py
        │   │   ├── property_location_changed.py
        │   │   ├── property_status_changed.py
        │   │   └── ...
        │   ├── repositories/                # ★ Interfaces (ABC) only
        │   │   ├── property_repository.py
        │   │   ├── property_search_repository.py
        │   │   ├── property_version_repository.py
        │   │   └── outbox_repository.py
        │   ├── services/
        │   │   ├── property_code_generator.py
        │   │   ├── slug_generator.py
        │   │   ├── property_validator.py
        │   │   └── property_merge_service.py
        │   ├── specifications/
        │   │   ├── base.py
        │   │   ├── active_property.py
        │   │   └── geo_specifications.py
        │   ├── factories/
        │   │   └── property_factory.py
        │   └── exceptions/
        │       ├── base.py
        │       ├── property_not_found.py
        │       ├── concurrency_conflict.py
        │       ├── invalid_status_transition.py
        │       └── validation_error.py
        │
        ├── application/                     # Use cases / orchestration
        │   ├── __init__.py
        │   ├── commands/
        │   │   ├── create_property.py
        │   │   ├── update_property.py
        │   │   ├── delete_property.py
        │   │   ├── bulk_import_properties.py
        │   │   ├── bulk_update_properties.py
        │   │   ├── bulk_delete_properties.py
        │   │   ├── change_property_status.py
        │   │   ├── update_property_images.py
        │   │   ├── update_property_documents.py
        │   │   └── register_from_source.py
        │   ├── queries/
        │   │   ├── get_property.py
        │   │   ├── search_properties.py
        │   │   ├── get_nearby_properties.py
        │   │   ├── get_property_history.py
        │   │   ├── get_property_versions.py
        │   │   └── get_property_statistics.py
        │   ├── handlers/                    # Command/Query handlers
        │   │   ├── command_handlers/
        │   │   └── query_handlers/
        │   ├── dto/                         # Application-level DTOs
        │   │   ├── property_create_dto.py
        │   │   ├── property_update_dto.py
        │   │   ├── property_search_dto.py
        │   │   └── bulk_operation_dto.py
        │   ├── services/
        │   │   ├── property_application_service.py
        │   │   ├── property_search_service.py
        │   │   ├── property_media_service.py
        │   │   └── property_import_service.py
        │   ├── unit_of_work.py              # UoW interface
        │   └── event_handlers/
        │       └── internal_event_handlers.py
        │
        ├── infrastructure/                  # ★ OUTERMOST — implements interfaces
        │   ├── __init__.py
        │   ├── persistence/
        │   │   ├── database.py              # Async engine, session factory
        │   │   ├── unit_of_work.py          # SQLAlchemy UoW impl
        │   │   ├── models/                  # SQLAlchemy ORM models
        │   │   │   ├── base.py
        │   │   │   ├── property_model.py
        │   │   │   ├── property_image_model.py
        │   │   │   ├── property_document_model.py
        │   │   │   ├── property_address_model.py
        │   │   │   ├── property_feature_model.py
        │   │   │   ├── property_amenity_model.py
        │   │   │   ├── property_price_history_model.py
        │   │   │   ├── property_status_history_model.py
        │   │   │   ├── property_ownership_model.py
        │   │   │   ├── property_tag_model.py
        │   │   │   ├── property_metadata_model.py
        │   │   │   ├── property_external_source_model.py
        │   │   │   ├── property_version_model.py
        │   │   │   ├── property_audit_log_model.py
        │   │   │   ├── outbox_event_model.py
        │   │   │   └── lookup_models.py
        │   │   ├── repositories/
        │   │   │   ├── sqlalchemy_property_repository.py
        │   │   │   ├── sqlalchemy_search_repository.py
        │   │   │   ├── sqlalchemy_version_repository.py
        │   │   │   └── sqlalchemy_outbox_repository.py
        │   │   └── mappers/                 # ORM ↔ Domain mappers
        │   │       └── property_mapper.py
        │   ├── cache/
        │   │   ├── redis_client.py
        │   │   ├── property_cache.py
        │   │   └── search_cache.py
        │   ├── messaging/
        │   │   ├── rabbitmq_publisher.py
        │   │   ├── event_serializer.py
        │   │   └── outbox_processor.py
        │   ├── storage/
        │   │   ├── object_storage.py        # S3/MinIO interface
        │   │   └── s3_storage.py
        │   ├── geocoding/
        │   │   ├── geocoding_client.py
        │   │   └── nominatim_adapter.py
        │   ├── external/
        │   │   └── listing_adapters/        # Anti-corruption layer
        │   │       ├── base.py
        │   │       └── sahibinden_adapter.py
        │   └── celery/
        │       ├── app.py
        │       ├── tasks/
        │       │   ├── image_processing.py
        │       │   ├── geocoding_tasks.py
        │       │   ├── import_tasks.py
        │       │   ├── sync_tasks.py
        │       │   └── outbox_tasks.py
        │       └── beat_schedule.py
        │
        ├── presentation/                    # HTTP layer
        │   ├── __init__.py
        │   ├── api/
        │   │   ├── v1/
        │   │   │   ├── router.py
        │   │   │   ├── properties.py
        │   │   │   ├── property_images.py
        │   │   │   ├── property_documents.py
        │   │   │   ├── property_search.py
        │   │   │   ├── property_history.py
        │   │   │   ├── property_versions.py
        │   │   │   ├── property_metadata.py
        │   │   │   ├── property_statistics.py
        │   │   │   └── bulk_operations.py
        │   │   └── deps.py                  # FastAPI dependencies
        │   ├── schemas/                     # Pydantic v2 request/response
        │   │   ├── property_schemas.py
        │   │   ├── search_schemas.py
        │   │   ├── media_schemas.py
        │   │   ├── bulk_schemas.py
        │   │   ├── common.py
        │   │   └── pagination.py
        │   ├── middleware/
        │   │   ├── correlation_id.py
        │   │   ├── request_logging.py
        │   │   └── rate_limiting.py
        │   └── exception_handlers.py
        │
        ├── shared/
        │   ├── __init__.py
        │   ├── types.py                     # Type aliases
        │   ├── pagination.py
        │   ├── idempotency.py
        │   └── utils/
        │       ├── datetime_utils.py
        │       └── geo_utils.py
        │
        └── di/                              # Dependency Injection container
            ├── __init__.py
            └── container.py                 # Wiring all layers
```

## Layer Rules

| Layer | May Import From | Must NOT Import |
|-------|-----------------|-----------------|
| `domain` | `domain` only | application, infrastructure, presentation |
| `application` | `domain`, `application` | infrastructure (except via interfaces), presentation |
| `infrastructure` | `domain`, `application`, `infrastructure` | presentation |
| `presentation` | all layers via DI | — |

## Module Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Packages | snake_case | `property_service` |
| Classes | PascalCase | `PropertyRepository` |
| Functions | snake_case | `get_property_by_id` |
| Constants | UPPER_SNAKE | `MAX_BULK_SIZE` |
| DB tables | snake_case plural | `properties`, `property_images` |
| API paths | kebab-case segments | `/api/v1/properties/nearby` |
| Event names | PascalCase past tense | `PropertyCreated` |
| Redis keys | colon-separated | `property:detail:{id}` |
| Celery queues | dot-separated | `property.image.process` |

## Key Design Decisions

1. **Separate ORM models from domain entities** — mappers translate between layers
2. **Command/Query split in application layer** — CQRS-ready without full split yet
3. **Repository interfaces in domain** — infrastructure implements them
4. **Pydantic schemas only in presentation** — application uses its own DTOs
5. **DI container at startup** — FastAPI `Depends()` wired through container
6. **Outbox in infrastructure** — domain events never know about RabbitMQ
