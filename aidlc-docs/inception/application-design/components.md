# Components — todo-mcp

## Component Overview

```
todo_mcp/
├── core/          # Settings, Pydantic schemas, shared types
├── db/            # SQLAlchemy models, repository, DB connection
│   └── migrations/  # Alembic migration scripts
└── api/           # FastMCP server, tool handlers, service layer
```

---

## Component: `core`

**Purpose**: Cross-cutting foundations — configuration, domain schemas, shared enums.

**Responsibilities**:
- Load and validate all environment configuration via `pydantic-settings`
- Define Pydantic v2 input/output schemas for every MCP tool
- Define shared enums (`Status`, `Priority`, `SortField`, `SortOrder`)
- Provide a single source of truth for domain types used by both `db` and `api` layers

**Modules**:
| Module | Responsibility |
|---|---|
| `core/config.py` | `Settings` class — DATABASE_URL, LOG_LEVEL, etc. |
| `core/schemas.py` | All Pydantic v2 request/response models |
| `core/enums.py` | `Status`, `Priority`, `SortField`, `SortOrder` enums |

---

## Component: `db`

**Purpose**: All database concerns — ORM models, connection/session management, repository pattern.

**Responsibilities**:
- Define SQLAlchemy 2.x async ORM models (`Todo`, `Subtask`)
- Manage async engine and session factory (asyncpg driver, connection pooling)
- Implement `TodoRepository` — all DB read/write operations
- Own Alembic migration configuration and scripts

**Modules**:
| Module | Responsibility |
|---|---|
| `db/models.py` | SQLAlchemy ORM models: `Todo`, `Subtask` |
| `db/database.py` | Async engine, `AsyncSessionLocal`, `get_session` context manager |
| `db/repository.py` | `TodoRepository` — all async CRUD + filter/sort/paginate queries |
| `db/migrations/` | Alembic `env.py`, `alembic.ini`, version scripts |

---

## Component: `api`

**Purpose**: MCP server entry point, tool definitions, and service orchestration layer.

**Responsibilities**:
- Configure and run the FastMCP server (stdio transport)
- Define all 6 MCP tool handlers (thin — delegate to service)
- `TodoService` — owns all business logic: soft-delete, restore, filter assembly, subtask constraint enforcement
- Structured JSON logging middleware / setup
- Global error handler — catches unexpected exceptions, returns safe MCP errors

**Modules**:
| Module | Responsibility |
|---|---|
| `api/server.py` | FastMCP app instantiation, logging setup, entry point |
| `api/tools.py` | 6 MCP tool handler functions (thin wrappers around service) |
| `api/service.py` | `TodoService` — business logic orchestration |
| `api/errors.py` | Structured MCP error types, global error handler |
