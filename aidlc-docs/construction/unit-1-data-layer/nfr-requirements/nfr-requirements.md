# NFR Requirements — Unit 1: Data Layer

## Scalability

| Requirement | Decision | Rationale |
|---|---|---|
| Concurrency model | Async throughout (SQLAlchemy 2.x async + asyncpg) | Single stdio process — async avoids blocking on DB I/O |
| Connection pooling | `pool_size=5`, `max_overflow=5` | Single-user local tool; minimal pool is sufficient |
| Growth path | No horizontal scaling planned | stdio transport, single-user; scale-up via pool size increase if needed |

## Performance

| Requirement | Decision |
|---|---|
| Query performance | Index on `todos.deleted_at`, `todos.status`, `todos.priority`, `todos.due_date` to support common filter combinations |
| Pagination | LIMIT/OFFSET with a separate COUNT query; acceptable for expected data volumes |
| No caching layer | Not needed — single-user, low concurrency |

## Availability

| Requirement | Decision |
|---|---|
| Postgres restart | Server reconnects via SQLAlchemy pool on next request (pool pre-ping enabled) |
| Migration safety | Alembic migrations are additive/backward-compatible; no destructive DDL without explicit version |
| No HA required | Single-user local tool; Postgres container restart is acceptable |

## Security — Applicable Rules (Unit 1)

| Rule | Status | Implementation |
|---|---|---|
| SECURITY-01 | Applicable | `DATABASE_URL` must use `postgresql+asyncpg://` (TLS option available via `?ssl=require` for non-local deployments); Postgres data volume encryption is a Docker host concern |
| SECURITY-03 | Applicable | Structured JSON logging in `api/server.py` (Unit 2) covers the application; repository must not log query parameters containing user data |
| SECURITY-05 | Applicable | All inputs validated via Pydantic v2 schemas before reaching repository; parameterised queries via SQLAlchemy (no string concatenation) |
| SECURITY-09 | Applicable | No default credentials in code; `DATABASE_URL` from environment variable only |
| SECURITY-10 | Applicable | `uv.lock` committed; pinned base image in Dockerfile; no unused dependencies |
| SECURITY-13 | Applicable | Pydantic v2 used for all deserialization — safe, schema-validated; no `pickle` or unsafe eval |
| SECURITY-15 | Applicable | All DB operations wrapped in `get_session()` context manager — commits on success, rolls back on exception; resources always released |
| SECURITY-02 | N/A | No load balancer or API gateway |
| SECURITY-04 | N/A | No HTML endpoints |
| SECURITY-06 | N/A | No IAM policies |
| SECURITY-07 | N/A for Unit 1 | Docker network config is a Unit 2 (Infrastructure Design) concern |
| SECURITY-08 | N/A | Single-user, no auth layer |
| SECURITY-11 | N/A for Unit 1 | Rate limiting N/A (stdio); defence-in-depth handled at Unit 2 service layer |
| SECURITY-12 | N/A | No user authentication |
| SECURITY-14 | Advisory | Log retention and alerting are operational concerns outside local Docker scope |

## Reliability

| Requirement | Decision |
|---|---|
| Transaction integrity | All multi-row writes (todo + subtasks) in a single transaction |
| Error propagation | Repository raises Python exceptions; service layer maps to domain errors; no swallowed exceptions |
| Pool pre-ping | `pool_pre_ping=True` on engine — detects stale connections before use |

## Maintainability

| Requirement | Decision |
|---|---|
| Code style | `ruff` for linting + formatting (replaces flake8 + black + isort) |
| Type checking | `mypy` in strict mode on `todo_mcp/` package |
| Test coverage | pytest + pytest-asyncio; repository integration tests against real Postgres (testcontainers-python) |
| PBT | Hypothesis partial mode — PBT-02 (round-trip), PBT-03 (invariants), PBT-07 (generators), PBT-08 (shrinking + seed), PBT-09 (framework) enforced |
| Migration discipline | Each schema change in its own Alembic revision; revisions reviewed before merge |

## PBT Requirements (Partial Mode)

| Rule | Requirement for Unit 1 |
|---|---|
| PBT-02 | Round-trip test: `TodoOut.model_validate(todo_out.model_dump())` == original for generated inputs |
| PBT-03 | Invariant: filtered list ⊆ unfiltered list; pagination total invariant |
| PBT-07 | Domain generators for `TodoOut`, `CreateTodoInput` respecting all field constraints |
| PBT-08 | Hypothesis shrinking enabled; seed logged on CI failure |
| PBT-09 | `hypothesis` declared in dev dependencies; documented in tech-stack-decisions.md |
