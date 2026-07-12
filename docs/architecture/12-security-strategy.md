# 12. Security Strategy

## Authentication

### JWT (Platform-Issued)

Property Service is a **resource server** — it validates JWTs issued by the FINWARD Identity Service (or finward-api during transition).

| Claim | Usage |
|-------|-------|
| `sub` | User ID → `actor_id` in audit logs |
| `tenant_id` | Tenant scope for all queries |
| `roles` | RBAC role list |
| `permissions` | Fine-grained permission list |
| `exp` | Token expiry validation |
| `iss` | Issuer validation |
| `aud` | Audience = `property-service` |

**Algorithm:** RS256 (asymmetric) — public key from JWKS endpoint.

```python
# Middleware flow
1. Extract Bearer token
2. Validate signature via JWKS
3. Check exp, iss, aud
4. Inject AuthContext into request state
```

### API Keys (Partner & Enterprise)

For machine-to-machine access:

| Header | Value |
|--------|-------|
| `X-API-Key` | API key string |
| `X-API-Secret` | HMAC signature (enterprise tier) |

API keys stored hashed in Identity Service; Property Service validates via Identity Service introspection endpoint or cached key registry in Redis.

**API Key scopes:** subset of permissions (e.g., `property:read`, `property:search`).

---

## Authorization (RBAC)

### Roles

| Role | Description |
|------|-------------|
| `platform_admin` | Full access across tenants |
| `tenant_admin` | Full access within tenant |
| `property_manager` | CRUD within tenant |
| `property_viewer` | Read-only within tenant |
| `partner_readonly` | Read public/partner properties only |
| `api_integration` | Scoped via API key permissions |

### Permissions

| Permission | Endpoints |
|------------|-----------|
| `property:create` | POST /properties, POST /register |
| `property:read` | GET /properties/{id}, GET /code, GET /slug |
| `property:update` | PUT, PATCH /properties/{id} |
| `property:delete` | DELETE, POST /restore |
| `property:search` | POST/GET /search, /nearby, /map |
| `property:bulk_import` | POST /bulk/import |
| `property:bulk_update` | PATCH /bulk/update |
| `property:bulk_delete` | DELETE /bulk |
| `property:manage_media` | Image/document endpoints |
| `property:verify_documents` | Document verification |
| `property:manage_ownership` | Ownership CRUD |
| `property:audit` | Audit log access |
| `property:statistics` | Statistics endpoint |

### Authorization Flow

```python
async def require_permission(permission: str):
    def dependency(auth: AuthContext = Depends(get_auth_context)):
        if permission not in auth.permissions:
            raise AuthorizationError(f"Missing permission: {permission}")
        return auth
    return dependency
```

### Tenant Isolation

Every repository query includes `tenant_id` from JWT:

```python
# Mandatory tenant filter
SELECT * FROM properties
WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
```

`platform_admin` may pass `X-Tenant-ID` header to operate on behalf of a tenant.

---

## Ownership Validation

For user-owned properties (B2C mobile app):

1. Property has `created_by` = user ID
2. Or user appears in `property_ownership.owner_external_id`
3. Or user has `tenant_admin` / `property_manager` role

```python
def can_modify_property(auth: AuthContext, property: Property) -> bool:
    if "property:update" not in auth.permissions:
        return False
    if auth.tenant_id != property.tenant_id:
        return False
    if auth.role in ("platform_admin", "tenant_admin", "property_manager"):
        return True
    return property.created_by == auth.user_id
```

---

## Data Protection

| Measure | Implementation |
|---------|---------------|
| Encryption at rest | PostgreSQL TDE / cloud provider encryption |
| Encryption in transit | TLS 1.3 everywhere |
| PII in ownership | Field-level access control; masked in partner API |
| Document access | Presigned URLs with short TTL (1 hour) |
| Audit trail | All mutations logged with actor, IP, correlation ID |
| Soft delete | Data retained for compliance; hard delete admin-only |

---

## Rate Limiting

Redis sliding window per client:

| Key Pattern | Limit |
|-------------|-------|
| `ratelimit:user:{user_id}` | Based on tier |
| `ratelimit:apikey:{key_id}` | Based on key tier |
| `ratelimit:ip:{ip}` | 60/min (unauthenticated) |

```python
# Middleware
async def rate_limit_middleware(request, call_next):
    key = f"ratelimit:{auth.client_id}"
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 60)
    if current > limit:
        raise RateLimitExceededError(retry_after=await redis.ttl(key))
```

Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`.

---

## Input Security

| Threat | Mitigation |
|--------|------------|
| SQL Injection | SQLAlchemy parameterized queries only |
| XSS | JSON API only; no HTML rendering |
| Mass assignment | Explicit Pydantic schemas; no `**kwargs` to domain |
| File upload abuse | MIME validation, size limits, presigned URLs (no direct upload to API) |
| SSRF (listing URL import) | URL allowlist per provider; no internal IP ranges |
| GeoJSON injection | Validate polygon coordinate bounds and complexity (max 1000 points) |
| Bulk abuse | Max items per request; async for large batches |

---

## Secrets Management

| Secret | Storage |
|--------|---------|
| DB credentials | Environment variables / Vault |
| Redis password | Environment variables / Vault |
| RabbitMQ credentials | Environment variables / Vault |
| S3 access keys | IAM roles (preferred) or Vault |
| JWT public key | JWKS endpoint (cached) |
| API key hashes | Identity Service |

**Never** commit secrets. `.env.example` with placeholder values only.

---

## Security Headers

```python
# Middleware response headers
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
Cache-Control: no-store (for authenticated endpoints)
```

---

## Audit Logging

Every mutation records:

```json
{
  "property_id": "uuid",
  "tenant_id": "uuid",
  "action": "property.updated",
  "actor_id": "uuid",
  "actor_type": "user",
  "changes": { "title": { "old": "...", "new": "..." } },
  "ip_address": "203.0.113.1",
  "user_agent": "FINWARD-Mobile/1.0",
  "correlation_id": "uuid",
  "created_at": "2026-06-30T12:00:00Z"
}
```

Audit logs are **append-only** and retained for 7 years (configurable per tenant compliance tier).

---

## Compliance Considerations

| Requirement | Approach |
|-------------|----------|
| GDPR right to erasure | Hard delete endpoint (admin) cascades all related data |
| KVKK (Turkey) | Data residency: EU/TR region deployment option |
| Data export | Bulk export endpoint (tenant_admin) |
| Access logs | Retained 90 days in structured logging backend |
