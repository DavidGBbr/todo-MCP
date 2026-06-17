# Unit of Work Dependencies — todo-mcp

## Dependency Matrix

| Unit | Depends On | Depended On By |
|---|---|---|
| Unit 1 — Data Layer | External: PostgreSQL, asyncpg, SQLAlchemy, Alembic, pydantic-settings | Unit 2 |
| Unit 2 — MCP Server + Infrastructure | Unit 1 (all of `todo_mcp/core/` and `todo_mcp/db/`) | — (entry point) |

**Development order**: Unit 1 → Unit 2 (sequential, no parallelism possible)

---

## Internal Package Dependencies

```
Unit 2: todo_mcp/api/
    │
    ├── imports todo_mcp/core/   (schemas, enums, config)
    └── imports todo_mcp/db/     (repository, session)
            │
            └── imports todo_mcp/core/  (enums, config)
```

---

## Shared Resources

| Resource | Owner | Consumers |
|---|---|---|
| PostgreSQL database | Docker Compose (both envs) | Unit 1 (migrations), Unit 2 (runtime) |
| `todo_mcp/core/schemas.py` | Unit 1 | Unit 2 (tool input/output types) |
| `todo_mcp/core/enums.py` | Unit 1 | Unit 1 (ORM models), Unit 2 (service + tools) |
| `todo_mcp/db/repository.py` | Unit 1 | Unit 2 (`TodoService`) |
| `todo_mcp/db/database.py` | Unit 1 | Unit 2 (`api/server.py` session setup) |

---

## Integration Points

| From | To | Interface |
|---|---|---|
| `api/service.py` | `db/repository.py` | `TodoRepository(session)` constructor + async methods |
| `api/server.py` | `db/database.py` | `get_session()` async context manager |
| `api/tools.py` | `core/schemas.py` | FastMCP tool input/output type annotations |
| `db/models.py` | `core/enums.py` | `Status`, `Priority` enum imports |
| `db/database.py` | `core/config.py` | `get_settings()` for `DATABASE_URL` and pool config |

---

## External Service Dependency

```
docker-compose.yml
┌─────────────────────┐        ┌──────────────────┐
│   todo-mcp server   │───────▶│   postgres:16    │
│  (stdio transport)  │  5432  │  (internal only) │
└─────────────────────┘        └──────────────────┘
        ▲
        │ spawned as subprocess
MCP Client (e.g. Claude Desktop)
```

PostgreSQL port 5432 is bound to the internal Docker network only — not published to the host (SECURITY-07).
