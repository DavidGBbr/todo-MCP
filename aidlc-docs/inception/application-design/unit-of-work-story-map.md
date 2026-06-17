# Unit of Work Story Map — todo-mcp

User Stories stage was skipped (single developer, unambiguous scope). This map uses functional capabilities derived from requirements instead.

---

## Unit 1 — Data Layer

| # | Capability | Module | Notes |
|---|---|---|---|
| 1.1 | Environment configuration | `core/config.py` | DATABASE_URL, LOG_LEVEL, pool settings via pydantic-settings |
| 1.2 | Domain enums | `core/enums.py` | Status, Priority, SortField, SortOrder |
| 1.3 | Pydantic schemas — inputs | `core/schemas.py` | CreateTodoInput, UpdateTodoInput, ListTodosInput, SubtaskInput |
| 1.4 | Pydantic schemas — outputs | `core/schemas.py` | TodoOut, ListTodosOut, SubtaskOut |
| 1.5 | ORM model: Todo | `db/models.py` | All required + optional fields, soft-delete column |
| 1.6 | ORM model: Subtask | `db/models.py` | Separate table, FK → todos, ON DELETE CASCADE |
| 1.7 | Async DB engine + session | `db/database.py` | asyncpg driver, connection pool, get_session() context manager |
| 1.8 | Repository: create | `db/repository.py` | Insert todo + subtasks in one transaction |
| 1.9 | Repository: get by ID | `db/repository.py` | Includes soft-deleted items |
| 1.10 | Repository: update | `db/repository.py` | Partial update, sets updated_at |
| 1.11 | Repository: soft delete | `db/repository.py` | Sets deleted_at = now() |
| 1.12 | Repository: restore | `db/repository.py` | Clears deleted_at |
| 1.13 | Repository: list with filters | `db/repository.py` | All filter/sort/pagination params, returns (items, total) |
| 1.14 | Initial DB migration | `db/migrations/` | Creates todos + subtasks tables |

---

## Unit 2 — MCP Server + Infrastructure

| # | Capability | Module | Notes |
|---|---|---|---|
| 2.1 | Domain error types | `api/errors.py` | TodoNotFoundError, TodoAlreadyDeletedError, TodoNotDeletedError |
| 2.2 | Global error handler | `api/errors.py` | Catches all exceptions → safe MCP error, no stack traces |
| 2.3 | Structured JSON logging | `api/server.py` | python-json-logger, stdout, LOG_LEVEL from config |
| 2.4 | FastMCP server setup | `api/server.py` | stdio transport, error handler registration, entry point |
| 2.5 | TodoService: create | `api/service.py` | Validates subtask depth (one level), delegates to repo |
| 2.6 | TodoService: get | `api/service.py` | Raises NotFoundError if missing |
| 2.7 | TodoService: update | `api/service.py` | Raises NotFoundError; enforces subtask depth constraint |
| 2.8 | TodoService: soft delete | `api/service.py` | Raises NotFoundError; raises AlreadyDeletedError if already deleted |
| 2.9 | TodoService: restore | `api/service.py` | Raises NotFoundError; raises NotDeletedError if not deleted |
| 2.10 | TodoService: list | `api/service.py` | Assembles filters, delegates to repo, computes total_pages |
| 2.11 | MCP tool: create_todo | `api/tools.py` | Thin handler; validates UUID if needed; calls service |
| 2.12 | MCP tool: get_todo | `api/tools.py` | Thin handler |
| 2.13 | MCP tool: update_todo | `api/tools.py` | Thin handler |
| 2.14 | MCP tool: delete_todo | `api/tools.py` | Thin handler |
| 2.15 | MCP tool: restore_todo | `api/tools.py` | Thin handler |
| 2.16 | MCP tool: list_todos | `api/tools.py` | Thin handler |
| 2.17 | Production Dockerfile | `Dockerfile` | Pinned base image, UV install, no `latest` tags |
| 2.18 | Production compose | `docker-compose.yml` | MCP server + Postgres, internal network, no published DB port |
| 2.19 | Dev compose | `docker-compose.dev.yml` | Extends prod, adds hot-reload (Watchfiles), source volume mount |

---

## Full Coverage Check

| Requirement | Covered By |
|---|---|
| UUID id, title, description, status, priority, due_date | 1.3, 1.5 |
| Optional: project, tags, assignee, effort, subtasks | 1.3, 1.5, 1.6 |
| create_todo tool | 1.8, 2.5, 2.11 |
| get_todo tool | 1.9, 2.6, 2.12 |
| update_todo tool | 1.10, 2.7, 2.13 |
| delete_todo (soft) | 1.11, 2.8, 2.14 |
| restore_todo | 1.12, 2.9, 2.15 |
| list_todos with filter/sort/pagination | 1.13, 2.10, 2.16 |
| Subtasks one level only | 2.5, 2.7 |
| Soft delete / archive | 1.5, 1.11, 1.12 |
| Standard input validation + structured errors | 1.3, 1.4, 2.1, 2.2 |
| PostgreSQL backend | 1.7, 1.14 |
| Alembic migrations | 1.14 |
| stdio transport | 2.4 |
| pydantic-settings config | 1.1 |
| Structured JSON logging | 2.3 |
| Production Docker image (pinned) | 2.17 |
| Dev compose with hot-reload | 2.19 |
