# Services — todo-mcp

## Service: `TodoService`

**Location**: `todo_mcp/api/service.py`

**Role**: Single orchestration layer between MCP tool handlers and the database repository. Owns all business logic so tool handlers remain thin I/O adapters.

### Responsibilities

| Responsibility | Detail |
|---|---|
| **Business rule enforcement** | Subtask one-level constraint, soft-delete guard (already deleted?), restore guard (not deleted?) |
| **Filter assembly** | Translates `ListTodosInput` into repository query parameters |
| **Pagination calculation** | Computes `total_pages` from `total` count returned by repository |
| **Schema mapping** | Converts ORM `Todo` / `Subtask` objects → `TodoOut` / `SubtaskOut` Pydantic models |
| **Error raising** | Raises typed domain errors (`TodoNotFoundError`, `TodoAlreadyDeletedError`, `TodoNotDeletedError`) that the global error handler in `api/errors.py` maps to structured MCP responses |

### Interaction Pattern

```
MCP Client
    │
    │  stdio (JSON-RPC)
    ▼
FastMCP (api/server.py)
    │
    │  calls tool handler
    ▼
Tool Handler (api/tools.py)   ← thin: validates UUID format, calls service
    │
    │  calls service method
    ▼
TodoService (api/service.py)  ← owns business logic
    │
    │  calls repository method
    ▼
TodoRepository (db/repository.py)  ← owns all SQL
    │
    │  asyncpg / SQLAlchemy
    ▼
PostgreSQL
```

### Session Lifecycle

- Each MCP tool invocation gets a fresh `AsyncSession` via `get_session()` context manager
- `TodoService` receives the session at construction time (dependency injection pattern)
- Session commits on success, rolls back on any exception — managed by `get_session()`

### Error Flow

```
TodoService raises TodoNotFoundError
    │
    ▼
api/errors.py global handler
    │
    ▼
Returns {"code": "TODO_NOT_FOUND", "message": "Todo <id> not found"} via MCP
```

No stack traces or internal details are ever returned to the MCP client.

---

## Service: Logging Infrastructure

**Location**: `todo_mcp/api/server.py` (setup) — applied across all components

**Role**: Configures structured JSON logging once at server startup; all components use the standard `logging` module.

### Responsibilities

- Configure `python-json-logger` (or `structlog`) at startup using `LOG_LEVEL` from `Settings`
- Emit logs to stdout (container-friendly)
- Every log record includes: `timestamp`, `level`, `message`, `logger`
- Tool handlers add `tool_name` to log context per invocation
- No PII, credentials, or sensitive data logged at any level
