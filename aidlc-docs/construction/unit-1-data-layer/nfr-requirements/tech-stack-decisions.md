# Tech Stack Decisions — Unit 1: Data Layer

## Runtime

| Component | Choice | Version | Rationale |
|---|---|---|---|
| Language | Python | 3.12 | Current stable; broad library support; pinned in pyproject.toml and Dockerfile |
| Package manager | UV | latest stable | Fast resolver, built-in venv, lock file support; replaces pip + venv |
| Lock file | `uv.lock` | — | Committed to VCS; used in Docker build (SECURITY-10) |

## Database

| Component | Choice | Version | Rationale |
|---|---|---|---|
| Database server | PostgreSQL | 16 (pinned Docker tag) | Chosen in requirements; supports ARRAY columns for tags, full ACID, reliable |
| ORM | SQLAlchemy | 2.x (async) | Industry standard; async-native in 2.x; clean query builder |
| Driver | asyncpg | latest stable | Native async PostgreSQL driver; best performance with SQLAlchemy async |
| Migrations | Alembic | latest stable | First-class SQLAlchemy integration; autogenerate + manual revision support |
| Pool config | `pool_size=5`, `max_overflow=5`, `pool_pre_ping=True` | — | Minimal for single-user; pre-ping detects stale connections |

## Validation & Configuration

| Component | Choice | Version | Rationale |
|---|---|---|---|
| Schema validation | Pydantic | v2 | FastMCP native; fast Rust-backed validators; declarative field constraints |
| Configuration | pydantic-settings | v2 | Type-safe env-var reading; validates DATABASE_URL, LOG_LEVEL at startup |

## Testing

| Component | Choice | Version | Rationale |
|---|---|---|---|
| Test runner | pytest | latest stable | Ecosystem standard; rich plugin support |
| Async test support | pytest-asyncio | latest stable | Runs async test functions natively |
| Test DB | testcontainers-python (`testcontainers[postgres]`) | latest stable | Spins up a real Postgres container per test session; faithful to production (ARRAY, transactions, etc.) |
| Property-based testing | Hypothesis | latest stable | PBT-09 requirement; best-in-class Python PBT framework; integrates with pytest |

## Code Quality

| Component | Choice | Version | Rationale |
|---|---|---|---|
| Linter + formatter | ruff | latest stable | Single tool replacing flake8 + black + isort; fast; enforces consistent style |
| Type checker | mypy | latest stable | Strict mode on `todo_mcp/`; catches type errors before runtime |

## Dependency Pinning (SECURITY-10)

- All dependencies declared in `pyproject.toml` with minimum version constraints
- `uv.lock` pins exact resolved versions for all direct and transitive dependencies
- Docker build uses `uv sync --frozen` to install exactly what is in the lock file
- No `latest` tags in Dockerfile base image — pinned to `python:3.12-slim-bookworm` (or equivalent digest)

## Deferred / Not Applicable

| Item | Status |
|---|---|
| Caching layer (Redis, etc.) | Not needed — single-user, low concurrency |
| Message queue | Not needed |
| Observability agent (OpenTelemetry) | Out of scope for this version |
| Vulnerability scanner | Recommended via `uv` + `pip-audit` in CI; documented in build instructions |
