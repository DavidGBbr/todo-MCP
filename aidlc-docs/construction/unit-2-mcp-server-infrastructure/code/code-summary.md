# Code Summary — Unit 2: MCP Server + Infrastructure

## Generated Files

### API Package (`todo_mcp/api/`)
| File | Purpose |
|---|---|
| `server.py` | FastMCP server factory, stdio entry point, structured JSON logging setup |
| `tools.py` | Six thin MCP tool handlers with per-call DB session and safe error wrapping |
| `service.py` | `TodoService` orchestration layer between tools and repository |
| `errors.py` | Structured MCP error payloads and safe `ToolError` conversion |
| `__init__.py` | Exposes `create_mcp_server()` |

### Infrastructure
| File | Purpose |
|---|---|
| `Dockerfile` | Pinned Python 3.12 slim image with pinned UV image copy and frozen dependency sync |
| `docker-compose.yml` | Production-style Postgres + MCP server composition on an internal network |
| `docker-compose.dev.yml` | Dev composition with source mount and `watchfiles` reload command |
| `.dockerignore` | Keeps local caches, docs, tests, and venv out of Docker build context |
| `.env.example` | Documents required compose environment variables |

### Tests
| File | Coverage |
|---|---|
| `tests/api/test_service.py` | Service mapping, soft-delete guard, restore guard, pagination metadata |
| `tests/api/test_tools.py` | Tool-level create/get/update/list/delete/restore cycle and structured UUID error |
| `tests/api/test_server.py` | FastMCP server registers exactly the six required tools |

## Adjusted Unit 1 Contracts

- `ListTodosInput.status` and `ListTodosInput.priority` now support one-or-more values while still accepting a single scalar input.
- `ListTodosInput` now includes `due_before` and `due_after` filters.
- `TodoRepository.list()` now applies status/priority `IN` filters and due-date range filters.
- Alembic `env.py` now respects externally injected `sqlalchemy.url` and normalizes it to asyncpg for async migrations.

## Verification Fixes

- Test engine fixture is function-scoped to avoid reusing asyncpg connections across closed Windows event loops.
- Hypothesis DB strategies exclude NUL bytes because PostgreSQL text fields reject them.
- Repository PBT tests clear tables per generated example to avoid fixture state leakage.
- `SortField.title_ = "title"` avoids the `str.title` typing conflict without changing the public wire value.

## Verification Results

| Check | Result |
|---|---|
| `python -m pytest` | 44 passed, 1 Alembic deprecation warning |
| `python -m ruff check .` | Passed |
| `python -m mypy todo_mcp` | Passed |
| `POSTGRES_PASSWORD=test-password docker compose config` | Passed |
| `POSTGRES_PASSWORD=test-password docker compose -f docker-compose.dev.yml config` | Passed |

## Next Step

Configure Claude Code as the MCP client to launch this stdio server with a real `DATABASE_URL` pointed at the Postgres service.
