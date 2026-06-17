# Code Summary — Unit 1: Data Layer

## Generated Files

### Project Setup
| File | Purpose |
|---|---|
| `pyproject.toml` | Python 3.12, UV, all dependencies declared |
| `alembic.ini` | Alembic entry point; `script_location = todo_mcp/db/migrations` |
| `todo_mcp/__init__.py` | Package root |
| `todo_mcp/core/__init__.py` | Core sub-package |
| `todo_mcp/db/__init__.py` | DB sub-package |
| `todo_mcp/api/__init__.py` | API placeholder — Unit 2 fills this |
| `tests/__init__.py` | Tests root |
| `tests/core/__init__.py` | Core tests sub-package |
| `tests/db/__init__.py` | DB tests sub-package |
| `tests/api/__init__.py` | API tests placeholder |

### Core Package (`todo_mcp/core/`)
| File | Key contents |
|---|---|
| `enums.py` | `Status`, `Priority`, `SortField`, `SortOrder` string enums |
| `config.py` | `Settings` (pydantic-settings); `get_settings()` LRU singleton |
| `exceptions.py` | `TodoNotFoundError`, `TodoAlreadyDeletedError`, `TodoNotDeletedError`, `PageOutOfRangeError` |
| `schemas.py` | `SubtaskInput`, `CreateTodoInput`, `UpdateTodoInput`, `ListTodosInput`; `SubtaskOut`, `TodoOut`, `ListTodosOut` |

### DB Package (`todo_mcp/db/`)
| File | Key contents |
|---|---|
| `models.py` | `Base`, `Todo` ORM model (ARRAY tags, TIMESTAMPTZ, selectinload subtasks), `Subtask` ORM model |
| `database.py` | `engine`, `AsyncSessionLocal`, `get_session()` async context manager |
| `repository.py` | `TodoRepository`: `create`, `get_by_id`, `update`, `soft_delete`, `restore`, `list` |

### Alembic Migrations (`todo_mcp/db/migrations/`)
| File | Purpose |
|---|---|
| `env.py` | Async Alembic env; reads `DATABASE_URL` from settings |
| `script.py.mako` | Revision template |
| `versions/001_initial_schema.py` | Creates `todos` + `subtasks` tables; 7 indexes (including GIN on tags); downgrade script |

### Tests (`tests/`)
| File | Coverage |
|---|---|
| `strategies.py` | Hypothesis strategies: `create_todo_input_strategy`, `list_todos_input_strategy`, `todo_out_strategy`, `subtask_out_strategy` |
| `conftest.py` | `postgres_container` (testcontainers Postgres 16), `db_url`, `alembic_upgrade` (session-scoped autouse), `engine`, `session` (per-test rollback) |
| `core/test_schemas.py` | Example-based: field validation, length limits, enum rejection, date validation; PBT-02 round-trip |
| `db/test_repository.py` | Example-based: create, get, update, subtask upsert, soft_delete, restore, list with filters/pagination, edge cases |
| `db/test_repository_pbt.py` | PBT-03: filter invariant, pagination invariant, soft-delete invariant |

## Key Implementation Decisions

### Subtask merge strategy (BR-10)
Passing `subtasks` in `UpdateTodoInput` **merges**: subtasks with a matching existing `id` are updated; subtasks with no matching `id` are inserted; subtasks not in the list are left untouched. Removal requires a future dedicated tool.

### Priority sort via CASE expression
PostgreSQL has no native enum ordering. The repository maps `high→0`, `medium→1`, `low→2` using a SQLAlchemy `case()` expression so `ORDER BY priority ASC` returns `high, medium, low` as required.

### Async engine module-level initialization
`engine` and `AsyncSessionLocal` are created at import time from `get_settings()`. Tests override the URL by pointing `alembic_upgrade` at the testcontainers URL — the production engine is never exercised in tests.

### Session-per-test rollback
Each test receives a session inside a started transaction. On teardown the session rolls back, giving full test isolation without truncating tables between tests.

### PAGE_OUT_OF_RANGE exception for `total == 0`
When `total == 0`, `total_pages == 0`. Requesting `page=1` with zero results is treated as valid (returns empty list). Only pages strictly greater than `total_pages` when `total > 0` raise `PageOutOfRangeError` (BR-12).
