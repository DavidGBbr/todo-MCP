# Component Dependencies — todo-mcp

## Dependency Matrix

| Component | Depends On | Depended On By |
|---|---|---|
| `core` | — (no internal deps) | `db`, `api` |
| `db` | `core` (schemas, enums, config) | `api` |
| `api` | `core` (schemas, enums), `db` (repository, session) | — (entry point) |

**Rule**: Dependencies flow strictly downward — `api` → `db` → `core`. No circular dependencies.

---

## Dependency Graph

```
+------------------+
|      api/        |
|  server.py       |
|  tools.py        |
|  service.py      |
|  errors.py       |
+--------+---------+
         |
         | imports schemas, enums        imports repository, session
         |                              |
         v                              v
+------------------+         +--------------------+
|      core/       |         |        db/         |
|  config.py       | <----   |  models.py         |
|  schemas.py      |         |  database.py       |
|  enums.py        |         |  repository.py     |
+------------------+         |  migrations/       |
                             +--------------------+
```

---

## Communication Patterns

### `api` → `db`
- **Pattern**: Direct async method calls — `TodoService` instantiates `TodoRepository(session)` and calls its methods
- **Session passing**: `AsyncSession` created by `get_session()` context manager in `api/server.py` per tool invocation; injected into `TodoRepository` constructor
- **Coupling**: `api/service.py` depends on `TodoRepository` interface only — not on SQLAlchemy internals

### `api` → `core`
- **Pattern**: Import — `api` imports Pydantic schemas and enums from `core` for tool input/output typing
- **Pattern**: Import — `api/server.py` imports `get_settings()` from `core/config.py` at startup

### `db` → `core`
- **Pattern**: Import — `db/models.py` imports `Status`, `Priority` enums from `core/enums.py`
- **Pattern**: Import — `db/database.py` imports `Settings` from `core/config.py` to read `DATABASE_URL` and pool settings

---

## Data Flow — `create_todo` Example

```
1. MCP client sends tool call: create_todo({title: ..., ...})
2. FastMCP deserialises args → CreateTodoInput (Pydantic validation in core/schemas.py)
3. tools.create_todo() calls TodoService.create_todo(data)
4. TodoService validates subtask constraint (one level only)
5. TodoService calls TodoRepository.create(data)
6. TodoRepository inserts Todo + Subtask rows inside AsyncSession transaction
7. TodoRepository returns ORM Todo object
8. TodoService maps Todo → TodoOut (core/schemas.py)
9. tools.create_todo() returns TodoOut to FastMCP
10. FastMCP serialises response → MCP client
```

---

## External Dependencies

| Dependency | Used By | Purpose |
|---|---|---|
| `fastmcp` | `api/server.py` | MCP server framework, stdio transport, tool registration |
| `sqlalchemy[asyncio]` | `db/` | ORM models, async session, query builder |
| `asyncpg` | `db/database.py` | Async PostgreSQL driver |
| `alembic` | `db/migrations/` | Schema migration management |
| `pydantic-settings` | `core/config.py` | Environment-based configuration |
| `pydantic` v2 | `core/schemas.py` | Request/response validation |
| `python-json-logger` | `api/server.py` | Structured JSON log output |
| `hypothesis` | test suite | Property-based testing (partial mode) |
| `pytest` + `pytest-asyncio` | test suite | Async test runner |
