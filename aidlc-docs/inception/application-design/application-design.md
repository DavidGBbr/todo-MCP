# Application Design — todo-mcp

## Summary of Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Service layer | Yes — `TodoService` | Business logic (soft-delete guards, filter assembly, schema mapping) isolated from tool handlers |
| Package layout | Layered subpackages | `core/`, `db/`, `api/` — clear separation of concerns, no circular deps |
| Configuration | `pydantic-settings` | Type-safe, env-var driven, validated at startup |
| Subtasks storage | Separate `subtasks` table | FK to `todos`, `ON DELETE CASCADE`, queryable individually |

---

## Package Structure

```
todo_mcp/
├── core/
│   ├── __init__.py
│   ├── config.py       # Settings (pydantic-settings)
│   ├── schemas.py      # All Pydantic v2 I/O schemas
│   └── enums.py        # Status, Priority, SortField, SortOrder
│
├── db/
│   ├── __init__.py
│   ├── models.py       # SQLAlchemy async ORM: Todo, Subtask
│   ├── database.py     # Engine, session factory, get_session()
│   ├── repository.py   # TodoRepository (all SQL)
│   └── migrations/
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
│
└── api/
    ├── __init__.py
    ├── server.py       # FastMCP app, logging setup, entry point
    ├── tools.py        # 6 MCP tool handlers (thin)
    ├── service.py      # TodoService (business logic)
    └── errors.py       # Domain errors, global error handler
```

---

## Components

See [components.md](components.md) for full component descriptions.

### `core` — Foundations
No internal dependencies. Provides `Settings`, Pydantic schemas, and enums to all other layers.

### `db` — Data Layer
Depends on `core`. Owns ORM models, async DB connection/pooling, repository (all SQL), and Alembic migrations.

### `api` — MCP Server + Service
Depends on `core` and `db`. Owns the FastMCP server, 6 tool handlers, `TodoService` business logic, logging setup, and error handling.

---

## Service Layer

See [services.md](services.md) for full service descriptions.

`TodoService` is the single orchestration point between tool handlers and `TodoRepository`:
- Enforces all business rules (soft-delete guard, restore guard, subtask depth constraint)
- Assembles filter/sort/pagination parameters for repository queries
- Maps ORM objects → Pydantic output schemas
- Raises typed domain errors (`TodoNotFoundError`, etc.) caught by the global error handler

---

## Component Dependencies

See [component-dependency.md](component-dependency.md) for dependency matrix and data flow.

Dependency direction (strict, no cycles):
```
api → db → core
api → core
```

---

## Method Signatures

See [component-methods.md](component-methods.md) for all method signatures and input/output types.

---

## Key Design Constraints

1. **No stack traces to MCP client** — global error handler in `api/errors.py` always returns a safe generic message
2. **Subtasks are one level only** — `TodoService.update_todo()` enforces this; `Subtask` model has no self-referencing FK
3. **Soft-delete only** — no permanent delete tool; `deleted_at` is the only deletion mechanism
4. **Async throughout** — all DB operations use `AsyncSession` + `asyncpg`; no sync SQLAlchemy calls
5. **Session per tool call** — `get_session()` context manager creates and closes a session for each MCP tool invocation
