# Code Generation Plan — Unit 1: Data Layer

## Unit Context

- **Unit**: Unit 1 — Data Layer
- **Workspace root**: `c:/Users/davidgb/Desktop/projetos/todo-mcp`
- **Project type**: Greenfield monolith
- **Code location**: workspace root (never aidlc-docs/)
- **Depends on**: none (Unit 2 depends on this unit)
- **Stories covered**: 1.1–1.14 (see unit-of-work-story-map.md)

---

## Steps

### Step 1 — Project Structure Setup
- [x] Create `pyproject.toml` (Python 3.12, UV, all dependencies pinned)
- [x] Create `alembic.ini`
- [x] Create `todo_mcp/__init__.py`
- [x] Create `todo_mcp/core/__init__.py`
- [x] Create `todo_mcp/db/__init__.py`
- [x] Create `todo_mcp/api/__init__.py` (placeholder — Unit 2 fills it)
- [x] Create `tests/__init__.py`
- [x] Create `tests/core/__init__.py`
- [x] Create `tests/db/__init__.py`
- [x] Create `tests/api/__init__.py` (placeholder)
- [x] Create `tests/strategies.py` (shared Hypothesis strategies)
- [x] Create `tests/conftest.py` (shared pytest fixtures)

### Step 2 — Core Package: Enums
- [x] Create `todo_mcp/core/enums.py`
  - `Status`, `Priority`, `SortField`, `SortOrder` enums
  - Stories: 1.2

### Step 3 — Core Package: Configuration
- [x] Create `todo_mcp/core/config.py`
  - `Settings` class via pydantic-settings
  - `get_settings()` cached singleton
  - Stories: 1.1

### Step 4 — Core Package: Schemas
- [x] Create `todo_mcp/core/schemas.py`
  - `SubtaskInput`, `CreateTodoInput`, `UpdateTodoInput`, `ListTodosInput`
  - `SubtaskOut`, `TodoOut`, `ListTodosOut`
  - All field constraints (max_length, ge/le, validators)
  - Stories: 1.3, 1.4

### Step 5 — DB Package: ORM Models
- [x] Create `todo_mcp/db/models.py`
  - `Base` declarative base
  - `Todo` model with all columns (ARRAY for tags, TIMESTAMPTZ)
  - `Subtask` model with FK + CASCADE
  - `selectinload` relationship on `Todo.subtasks`
  - Stories: 1.5, 1.6

### Step 6 — DB Package: Database Connection
- [x] Create `todo_mcp/db/database.py`
  - `create_engine()` with pool_size=5, max_overflow=5, pool_pre_ping=True
  - `AsyncSessionLocal` session factory
  - `get_session()` async context manager
  - Stories: 1.7

### Step 7 — DB Package: Repository
- [x] Create `todo_mcp/db/repository.py`
  - `TodoRepository` class
  - `create()`, `get_by_id()`, `update()`, `soft_delete()`, `restore()`, `list()` methods
  - Subtask merge/upsert logic in `update()`
  - Filter/sort/paginate logic in `list()`
  - Stories: 1.8–1.13

### Step 8 — Alembic Migration
- [x] Create `todo_mcp/db/migrations/env.py`
- [x] Create `todo_mcp/db/migrations/script.py.mako`
- [x] Create `todo_mcp/db/migrations/versions/001_initial_schema.py`
  - `todos` table + `subtasks` table
  - All indexes including GIN on tags
  - Downgrade script
  - Stories: 1.14

### Step 9 — Tests: Shared Strategies & Fixtures
- [x] Create `tests/strategies.py`
  - `todo_out_strategy()`, `create_todo_input_strategy()`, `list_todos_input_strategy()`
  - All strategies respect field constraints
- [x] Create `tests/conftest.py`
  - `postgres_container` session-scoped fixture (testcontainers)
  - `engine` + `session` fixtures
  - `alembic_upgrade` autouse session fixture

### Step 10 — Tests: Core Schema Tests
- [x] Create `tests/core/test_schemas.py`
  - Example-based: valid/invalid field values, enum rejection, max-length enforcement
  - PBT (PBT-02): round-trip `TodoOut.model_validate(todo_out.model_dump()) == todo_out`

### Step 11 — Tests: Repository Integration Tests
- [x] Create `tests/db/test_repository.py`
  - Example-based: create, get, update, soft_delete, restore, list with filters
  - Edge cases: not-found, already-deleted, not-deleted, out-of-range page, subtask merge
- [x] Create `tests/db/test_repository_pbt.py`
  - PBT (PBT-03): filter invariant — filtered ⊆ unfiltered
  - PBT (PBT-03): pagination invariant — sum of pages == total
  - PBT (PBT-03): soft-delete invariant — deleted items absent unless include_deleted=True

### Step 12 — Code Summary Documentation
- [x] Create `aidlc-docs/construction/unit-1-data-layer/code/code-summary.md`
  - List all generated files with paths
  - Note key implementation decisions
