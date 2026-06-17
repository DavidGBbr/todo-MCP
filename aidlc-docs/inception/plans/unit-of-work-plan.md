# Unit of Work Plan — todo-mcp

## Context

Two units were established in Workflow Planning and confirmed by Application Design:

| Unit | Packages | Description |
|---|---|---|
| **Unit 1 — Data Layer** | `todo_mcp/core/`, `todo_mcp/db/` | Settings, schemas, enums, ORM models, DB connection, repository, Alembic migrations |
| **Unit 2 — MCP Server + Infrastructure** | `todo_mcp/api/`, Docker files | FastMCP server, 6 tool handlers, TodoService, error handling, Dockerfile, docker-compose.yml, docker-compose.dev.yml |

Development sequence: Unit 1 first (Unit 2 depends on it).

---

## Plan Checkboxes

- [x] Confirm unit boundaries (settled in Workflow Planning + Application Design)
- [x] Answer open question below
- [x] Generate unit-of-work.md
- [x] Generate unit-of-work-dependency.md
- [x] Generate unit-of-work-story-map.md
- [x] Validate unit completeness

---

## Open Question

### Question 1
Where should the test suite live?

A) Top-level `tests/` directory mirroring the package structure (`tests/core/`, `tests/db/`, `tests/api/`)
B) Inline alongside source — each package has its own `tests/` subfolder (`todo_mcp/db/tests/`, `todo_mcp/api/tests/`)
X) Other (please describe after [Answer]: tag below)

[Answer]: option A
