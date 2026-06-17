# Logical Components — Unit 1: Data Layer

No external infrastructure components (queues, caches, circuit breakers) are required for Unit 1. The logical components are all in-process.

---

## Component: Async Engine & Session Factory

**Module**: `todo_mcp/db/database.py`

**Responsibility**: Owns the single shared `AsyncEngine` instance and the `AsyncSessionLocal` session factory. Exposes `get_session()` as the sole entry point for obtaining a DB session.

**Configuration**:
```
engine = create_async_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    echo=False,          # set True via LOG_LEVEL=DEBUG only
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

**Lifecycle**:
- Engine created once at startup
- `get_session()` yields a new `AsyncSession` per call, commits on exit, rolls back on exception
- Engine disposed on server shutdown

---

## Component: ORM Model Layer

**Module**: `todo_mcp/db/models.py`

**Responsibility**: Declares the SQLAlchemy 2.x mapped classes (`Todo`, `Subtask`) that define the DB schema. Used by Alembic for migration autogeneration and by the repository for query building.

**Key design points**:
- `Todo.tags` mapped as `ARRAY(Text)` (PostgreSQL-native)
- `Todo.subtasks` relationship with `lazy="selectin"` — always eager-loaded
- `Subtask.todo_id` has `ForeignKey("todos.id", ondelete="CASCADE")`
- All timestamp columns use `timezone=True` (UTC stored in DB)

---

## Component: TodoRepository

**Module**: `todo_mcp/db/repository.py`

**Responsibility**: Encapsulates all SQL operations. Receives an `AsyncSession` at construction; never creates its own sessions. Returns ORM model instances to the caller.

**Methods and their DB operations**:

| Method | SQL operations |
|---|---|
| `create` | `INSERT INTO todos` + `INSERT INTO subtasks` (batch) in one transaction |
| `get_by_id` | `SELECT todos + subtasks WHERE id = :id` (selectinload) |
| `update` | `UPDATE todos SET ... WHERE id = :id`; subtask upsert loop |
| `soft_delete` | `UPDATE todos SET deleted_at = now(), updated_at = now() WHERE id = :id` |
| `restore` | `UPDATE todos SET deleted_at = NULL, updated_at = now() WHERE id = :id` |
| `list` | `SELECT COUNT(*)` + `SELECT todos + subtasks WHERE <filters> ORDER BY <sort> LIMIT/OFFSET` |

---

## Component: Pydantic Schema Layer

**Module**: `todo_mcp/core/schemas.py`

**Responsibility**: Validates all input at the boundary before it reaches the repository. Maps ORM objects to typed output models for the service layer.

**Key validators**:
- `title`: `min_length=1`, `max_length=255`
- `due_date`: `date` type — Pydantic parses and validates ISO 8601 automatically
- `status` / `priority`: Python `Enum` — invalid values raise `ValidationError` at parse time
- `page`: `ge=1`; `page_size`: `ge=1, le=100`
- Each tag: `max_length=100`

---

## Component: Alembic Migration Engine

**Module**: `todo_mcp/db/migrations/`

**Responsibility**: Tracks schema state and applies incremental DDL changes.

**Initial migration (revision 001)**:
```sql
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    priority VARCHAR(10) NOT NULL,
    due_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ,
    project VARCHAR(255),
    tags TEXT[] NOT NULL DEFAULT '{}',
    assignee VARCHAR(255),
    effort VARCHAR(100)
);

CREATE TABLE subtasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    todo_id UUID NOT NULL REFERENCES todos(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);

-- Indexes
CREATE INDEX ix_todos_deleted_at ON todos (deleted_at);
CREATE INDEX ix_todos_status     ON todos (status);
CREATE INDEX ix_todos_priority   ON todos (priority);
CREATE INDEX ix_todos_due_date   ON todos (due_date);
CREATE INDEX ix_todos_project    ON todos (project);
CREATE INDEX ix_todos_assignee   ON todos (assignee);
CREATE INDEX ix_todos_tags       ON todos USING GIN (tags);
```

---

## Component: Settings

**Module**: `todo_mcp/core/config.py`

**Responsibility**: Reads and validates all environment configuration at startup. Fails fast with a clear error if required vars are missing or malformed.

**Fields**:
```python
class Settings(BaseSettings):
    database_url: PostgresDsn          # required — no default
    log_level: str = "INFO"
    db_pool_size: int = 5
    db_max_overflow: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
```

**Security note**: `database_url` is never logged or exposed in error messages (SECURITY-09).

---

## Test Infrastructure Components

| Component | Role |
|---|---|
| `testcontainers[postgres]` | Spins up a real Postgres 16 container for the test session; provides a `TEST_DATABASE_URL` |
| `pytest` fixtures in `tests/conftest.py` | Creates engine + session per test; runs `alembic upgrade head` once per session; rolls back each test in a transaction |
| `tests/strategies.py` | Hypothesis strategies for `Todo`, `CreateTodoInput`, `ListTodosInput` — shared across all PBT tests |
