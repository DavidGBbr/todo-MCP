# NFR Requirements Plan — Unit 1: Data Layer

## Plan Checkboxes

- [x] Answer open questions below
- [x] Generate nfr-requirements.md
- [x] Generate tech-stack-decisions.md
- [x] Validate completeness

---

## Pre-settled from INCEPTION (no questions needed)

| NFR Area | Decision |
|---|---|
| Database | PostgreSQL (asyncpg driver, SQLAlchemy 2.x async, connection pooling) |
| Migrations | Alembic |
| Validation | Pydantic v2 (type-safe, declarative) |
| Configuration | pydantic-settings reading from environment variables |
| Security baseline | Full enforcement — SECURITY-01, 03, 05, 09, 10, 13, 15 applicable to Unit 1 |
| PBT framework | Hypothesis (partial mode: PBT-02, 03, 07, 08, 09 enforced) |
| Transport | N/A for Unit 1 — no HTTP endpoints |
| Auth | N/A — single-user stdio |

---

## Open Questions

Please fill in the letter choice after each `[Answer]:` tag, then let me know when done.

---

### Question 1
What Python version should be pinned as the minimum in `pyproject.toml` and the Dockerfile base image?

A) Python 3.12 (current stable, widely available)
B) Python 3.13 (latest stable as of 2025)
X) Other (please describe after [Answer]: tag below)

[Answer]: option A

---

### Question 2
What connection pool size should be configured for the asyncpg pool?

A) Small — `pool_size=5`, `max_overflow=5` (fine for a single-user local tool)
B) Medium — `pool_size=10`, `max_overflow=10` (headroom if load increases slightly)
X) Other (please specify exact values after [Answer]: tag below)

[Answer]: option A

---

### Question 3
Should the test suite use a **real PostgreSQL instance** (via Docker / testcontainers) or a **SQLite in-memory DB** for repository integration tests?

A) Real PostgreSQL via `pytest-docker` or `testcontainers-python` (faithful to production behaviour — array columns, JSONB, etc. work correctly)
B) SQLite in-memory (faster setup, no Docker required for tests, but diverges from Postgres behaviour)
X) Other (please describe after [Answer]: tag below)

[Answer]: option A
