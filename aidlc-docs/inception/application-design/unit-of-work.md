# Unit of Work — todo-mcp

## Project Type: Greenfield Monolith (single deployable service)

Two sequential units of work. Unit 1 must be complete before Unit 2 begins (hard dependency).

---

## Unit 1 — Data Layer

**Scope**: Everything below the service layer — the foundation all other code builds on.

### Packages
| Package | Modules |
|---|---|
| `todo_mcp/core/` | `config.py`, `schemas.py`, `enums.py` |
| `todo_mcp/db/` | `models.py`, `database.py`, `repository.py`, `migrations/` |

### Deliverables
- `Settings` class via `pydantic-settings` reading `DATABASE_URL`, `LOG_LEVEL`, pool config
- `Status`, `Priority`, `SortField`, `SortOrder` enums
- All Pydantic v2 request/response schemas (`CreateTodoInput`, `UpdateTodoInput`, `ListTodosInput`, `TodoOut`, `ListTodosOut`, `SubtaskInput`, `SubtaskOut`)
- SQLAlchemy 2.x async ORM models: `Todo`, `Subtask` (separate table, FK + CASCADE)
- Async engine factory + `get_session()` context manager (asyncpg, connection pooling)
- `TodoRepository` with all async CRUD + filter/sort/paginate methods
- Alembic migration: initial schema (`todos` table + `subtasks` table)

### Test scope
```
tests/
├── core/
│   └── test_schemas.py      # Pydantic validation, enum constraints
└── db/
    ├── test_repository.py   # Integration tests against real Postgres
    └── test_schemas_pbt.py  # Hypothesis round-trip + invariant tests
```

### Exit criteria
- All ORM models map to valid Postgres schema
- `alembic upgrade head` runs clean on a fresh DB
- `TodoRepository` CRUD + filter tests pass against a test Postgres instance
- PBT round-trip test: `TodoOut(**todo.dict())` round-trips correctly for generated inputs

---

## Unit 2 — MCP Server + Infrastructure

**Scope**: Everything above the data layer — the MCP surface, business logic, and all Docker artefacts.

**Prerequisite**: Unit 1 complete and passing.

### Packages
| Package | Modules |
|---|---|
| `todo_mcp/api/` | `server.py`, `tools.py`, `service.py`, `errors.py` |
| Root | `Dockerfile`, `docker-compose.yml`, `docker-compose.dev.yml`, `pyproject.toml`, `uv.lock` |

### Deliverables
- `TodoService` with all business logic (soft-delete guard, restore guard, subtask depth constraint, filter assembly, schema mapping)
- 6 FastMCP tool handlers: `create_todo`, `get_todo`, `update_todo`, `delete_todo`, `restore_todo`, `list_todos`
- Structured JSON logging setup (`python-json-logger`) at server startup
- Global error handler — catches all unhandled exceptions, returns safe MCP errors
- Typed domain errors: `TodoNotFoundError`, `TodoAlreadyDeletedError`, `TodoNotDeletedError`
- Production `Dockerfile` — pinned base image, UV install, no `latest` tags
- `docker-compose.yml` — MCP server + Postgres service, internal network only
- `docker-compose.dev.yml` — adds hot-reload (Watchfiles), mounts source, same Postgres service

### Test scope
```
tests/
└── api/
    ├── test_service.py      # Unit tests for TodoService business rules
    ├── test_tools.py        # Integration tests: tool handler → service → DB
    └── test_service_pbt.py  # Hypothesis stateful + invariant tests
```

### Exit criteria
- All 6 MCP tools callable and return correct schemas
- Soft-delete + restore cycle works end-to-end
- Filter/sort/pagination returns correct subsets
- `docker-compose up` brings up Postgres + server; server connects successfully
- Dev compose hot-reload triggers on source file change
- Security baseline compliance verified (SECURITY-03, 05, 09, 10, 13, 15)

---

## Code Organisation Strategy (Greenfield)

```
todo-mcp/                          ← workspace root (application code here)
├── todo_mcp/                      ← main package
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   └── enums.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── repository.py
│   │   └── migrations/
│   │       ├── env.py
│   │       ├── script.py.mako
│   │       └── versions/
│   └── api/
│       ├── __init__.py
│       ├── server.py
│       ├── tools.py
│       ├── service.py
│       └── errors.py
├── tests/
│   ├── conftest.py            ← shared fixtures (DB session, test client)
│   ├── core/
│   │   └── test_schemas.py
│   ├── db/
│   │   ├── test_repository.py
│   │   └── test_schemas_pbt.py
│   └── api/
│       ├── test_service.py
│       ├── test_tools.py
│       └── test_service_pbt.py
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── docker-compose.dev.yml
```
