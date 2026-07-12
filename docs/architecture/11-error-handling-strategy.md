# 11. Error Handling Strategy

## Error Taxonomy

### Hierarchy

```
PropertyServiceError (base)
├── DomainError
│   ├── PropertyNotFoundError
│   ├── ConcurrencyConflictError
│   ├── InvalidStatusTransitionError
│   ├── ValidationError
│   ├── DuplicatePropertyError
│   ├── ImmutableFieldError
│   └── PropertyDeletedError
├── ApplicationError
│   ├── TenantMismatchError
│   ├── BulkLimitExceededError
│   ├── ImportJobFailedError
│   └── IdempotencyConflictError
├── InfrastructureError
│   ├── DatabaseError
│   ├── CacheError
│   ├── MessagingError
│   ├── StorageError
│   └── GeocodingError
└── PresentationError
    ├── AuthenticationError
    ├── AuthorizationError
    └── RateLimitExceededError
```

---

## Error Code Registry

| Code | HTTP | Layer | Description |
|------|------|-------|-------------|
| `VALIDATION_ERROR` | 400 | Presentation | Pydantic input validation failed |
| `PROPERTY_NOT_FOUND` | 404 | Domain | Property does not exist or not in tenant scope |
| `PROPERTY_DELETED` | 410 | Domain | Property is soft-deleted |
| `CONCURRENCY_CONFLICT` | 409 | Domain | Optimistic lock version mismatch |
| `DUPLICATE_PROPERTY` | 409 | Domain | Duplicate code, slug, or listing |
| `DUPLICATE_LISTING` | 409 | Domain | Provider + listing_id already exists |
| `INVALID_STATUS_TRANSITION` | 422 | Domain | Status state machine violation |
| `IMMUTABLE_FIELD` | 422 | Domain | Attempt to change immutable field |
| `LOCATION_REQUIRED` | 422 | Domain | Missing address and coordinates |
| `TYPE_CATEGORY_MISMATCH` | 422 | Domain | Property type doesn't match category |
| `AREA_INVALID` | 422 | Domain | net_area > gross_area |
| `PRICE_REQUIRED_FOR_LISTING` | 422 | Domain | Listed without price |
| `IMAGE_REQUIRED_FOR_LISTING` | 422 | Domain | Listed without images |
| `OWNERSHIP_EXCEEDS_100` | 422 | Domain | Ownership percentages sum > 100 |
| `TENANT_MISMATCH` | 403 | Application | Cross-tenant access attempt |
| `FORBIDDEN` | 403 | Presentation | Missing RBAC permission |
| `UNAUTHORIZED` | 401 | Presentation | Invalid or missing JWT |
| `RATE_LIMIT_EXCEEDED` | 429 | Presentation | Too many requests |
| `IDEMPOTENCY_CONFLICT` | 409 | Application | Same key, different payload |
| `BULK_LIMIT_EXCEEDED` | 422 | Application | Bulk operation too large |
| `IMPORT_JOB_FAILED` | 500 | Application | Bulk import job failure |
| `UNSUPPORTED_PROVIDER` | 422 | Application | Unknown listing provider |
| `GEOCODING_FAILED` | 502 | Infrastructure | External geocoding service error |
| `STORAGE_ERROR` | 502 | Infrastructure | Object storage failure |
| `INTERNAL_ERROR` | 500 | — | Unhandled exception |
| `SERVICE_UNAVAILABLE` | 503 | Infrastructure | Dependency down (DB, Redis) |

---

## Exception Classes (Domain)

```python
class PropertyServiceError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        details: list[ErrorDetail] | None = None,
    ):
        self.message = message
        self.code = code
        self.details = details or []

class PropertyNotFoundError(PropertyServiceError):
    def __init__(self, property_id: UUID):
        super().__init__(
            message=f"Property with id '{property_id}' was not found",
            code="PROPERTY_NOT_FOUND",
        )

class ConcurrencyConflictError(PropertyServiceError):
    def __init__(self, property_id: UUID, expected: int, actual: int):
        super().__init__(
            message=f"Property '{property_id}' was modified. Expected version {expected}, found {actual}",
            code="CONCURRENCY_CONFLICT",
        )
```

---

## FastAPI Exception Handlers

```python
# presentation/exception_handlers.py

async def property_service_error_handler(
    request: Request, exc: PropertyServiceError
) -> JSONResponse:
    status_code = ERROR_CODE_TO_HTTP.get(exc.code, 500)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": [d.model_dump() for d in exc.details],
                "correlation_id": request.state.correlation_id,
            }
        },
    )

async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        ErrorDetail(
            field=".".join(str(loc) for loc in e["loc"]),
            message=e["msg"],
            code="VALIDATION_ERROR",
        )
        for e in exc.errors()
    ]
    return JSONResponse(status_code=400, content={...})

async def unhandled_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.exception("Unhandled error", correlation_id=request.state.correlation_id)
    return JSONResponse(status_code=500, content={
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "correlation_id": request.state.correlation_id,
        }
    })
```

---

## Error Handling by Layer

| Layer | Strategy |
|-------|----------|
| **Presentation** | Catch domain/application errors → map to HTTP; never expose stack traces |
| **Application** | Catch infrastructure errors → wrap in ApplicationError; let domain errors propagate |
| **Domain** | Raise typed domain exceptions; no HTTP knowledge |
| **Infrastructure** | Catch DB/storage/messaging errors → raise InfrastructureError; log with context |

---

## Retry & Circuit Breaker

| External Dependency | Retry | Circuit Breaker |
|--------------------|-------|-----------------|
| PostgreSQL | Connection pool retry (3x) | Pool health check |
| Redis | 2 retries, 50ms backoff | Fallback: skip cache |
| RabbitMQ | 3 retries in outbox processor | Alert on DLQ growth |
| Geocoding API | 2 retries, exponential backoff | Open after 5 failures / 60s |
| Object Storage (S3) | 3 retries (boto built-in) | Fail upload endpoint |

---

## Logging on Errors

```python
logger.error(
    "Property update failed",
    extra={
        "correlation_id": correlation_id,
        "property_id": str(property_id),
        "tenant_id": str(tenant_id),
        "error_code": exc.code,
        "actor_id": str(actor_id),
    },
    exc_info=isinstance(exc, InfrastructureError),
)
```

- **4xx errors:** Log at WARNING level
- **5xx errors:** Log at ERROR with stack trace
- **Never log:** JWT tokens, PII in ownership fields, full document contents

---

## Client Retry Guidance (documented in OpenAPI)

| HTTP Code | Client Should Retry? |
|-----------|---------------------|
| 400 | No — fix request |
| 401 | No — re-authenticate |
| 403 | No |
| 404 | No |
| 409 (concurrency) | Yes — fetch latest, merge, retry |
| 409 (idempotency) | No — use new key |
| 422 | No — fix business rule violation |
| 429 | Yes — after `Retry-After` header |
| 500 | Yes — with exponential backoff (max 3) |
| 503 | Yes — with exponential backoff |
