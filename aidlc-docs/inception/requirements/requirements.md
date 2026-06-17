# Requirements — todo-mcp

## Intent Analysis

| Field | Value |
|---|---|
| **User Request** | Build a minimal MCP server to manage a todo-list with Python + UV, FastMCP, and Docker |
| **Request Type** | New Project (Greenfield) |
| **Scope Estimate** | Single Component — one MCP server with a PostgreSQL backend |
| **Complexity Estimate** | Moderate — new data model, MCP protocol, Docker multi-container setup, soft-delete, filtering/sorting/pagination |

---

## Functional Requirements

### FR-01: Todo Item Data Model

Every todo item MUST have the following **required** fields:

| Field | Type | Constraints |
|---|---|---|
| `id` | UUID v4 | Auto-generated on creation, immutable |
| `title` | string | Required, max 255 chars |
| `description` | string | Required, may be empty string |
| `status` | enum | `to_do` \| `in_progress` \| `blocked` \| `done` |
| `priority` | enum | `high` \| `medium` \| `low` |
| `due_date` | date (ISO 8601) | Required |
| `created_at` | datetime | Auto-set on creation, immutable |
| `updated_at` | datetime | Auto-updated on every mutation |
| `deleted_at` | datetime \| null | Null = active; set = soft-deleted |

Every todo item MAY have the following **optional** fields:

| Field | Type | Constraints |
|---|---|---|
| `project` | string \| null | Parent category (e.g. "Work", "Home") |
| `tags` | string[] | Context labels (e.g. "@computer", "@calls") |
| `assignee` | string \| null | Person responsible |
| `effort` | string \| null | Free-text estimate (e.g. "30 minutes", "2 hours") |
| `subtasks` | Subtask[] | One level deep only — subtasks cannot have subtasks |

**Subtask model** (one level only):

| Field | Type | Constraints |
|---|---|---|
| `id` | UUID v4 | Auto-generated, immutable |
| `title` | string | Required, max 255 chars |
| `done` | boolean | Default false |

---

### FR-02: MCP Tools (CRUD)

The server MUST expose the following MCP tools:

| Tool | Description |
|---|---|
| `create_todo` | Create a new todo item with required fields and optional fields |
| `get_todo` | Retrieve a single active todo by ID |
| `update_todo` | Partially update any mutable field(s) of an existing todo |
| `delete_todo` | Soft-delete a todo (set `deleted_at`, hide from normal queries) |
| `restore_todo` | Restore a soft-deleted todo (clear `deleted_at`) |
| `list_todos` | List active todos with filtering, sorting, and pagination |

---

### FR-03: Filtering, Sorting, and Pagination

`list_todos` MUST support:

**Filters** (all optional, combinable):
- `status` — one or more status values
- `priority` — one or more priority values
- `project` — exact match
- `tags` — any-of match (todo has at least one of the given tags)
- `assignee` — exact match
- `due_before` — ISO 8601 date (inclusive)
- `due_after` — ISO 8601 date (inclusive)
- `include_deleted` — boolean, default false

**Sorting:**
- `sort_by` — field name: `created_at`, `updated_at`, `due_date`, `priority`, `title`
- `sort_order` — `asc` \| `desc`, default `asc`

**Pagination:**
- `page` — 1-based page number, default 1
- `page_size` — items per page, default 20, max 100

Response MUST include: `items`, `total`, `page`, `page_size`, `total_pages`.

---

### FR-04: Soft Delete and Restore

- `delete_todo` MUST set `deleted_at` to the current UTC timestamp; the item remains in the database
- Soft-deleted items MUST NOT appear in `list_todos` unless `include_deleted=true`
- `get_todo` MUST return soft-deleted items (with `deleted_at` populated) so callers can inspect them
- `restore_todo` MUST clear `deleted_at` and update `updated_at`

---

### FR-05: Input Validation and Error Handling (Standard)

- All required fields MUST be validated on creation; missing or null required fields return a structured MCP error
- Enum fields (`status`, `priority`) MUST reject values outside the defined set
- `due_date` MUST parse as a valid ISO 8601 date
- UUIDs in tool arguments MUST be validated as valid UUID v4 format
- String fields MUST enforce max-length constraints
- Error responses MUST include a human-readable `message` and a machine-readable `code`
- A global error handler MUST catch unexpected exceptions and return a safe generic error (no stack traces exposed)

---

## Non-Functional Requirements

### NFR-01: Storage — PostgreSQL

- Persistence backend: **PostgreSQL** (running as a separate Docker container)
- The MCP server connects to Postgres via an environment variable (`DATABASE_URL`)
- Schema migrations MUST be managed with a migration tool (Alembic recommended for Python)
- Connection pooling SHOULD be used (e.g. SQLAlchemy with asyncpg)

### NFR-02: MCP Transport — stdio

- The server uses **stdio transport** exclusively
- This means the server is launched as a subprocess by the MCP client (e.g. Claude Desktop)
- No HTTP port is exposed by the MCP server itself
- The PostgreSQL container IS network-accessible but only within the Docker Compose network

### NFR-03: Authentication

- **Single-user, no authentication** — the stdio process boundary is the access control layer
- No login, tokens, or sessions are implemented
- SECURITY-08 (deny-by-default auth) and SECURITY-12 (password/MFA) are **N/A** for this project due to stdio transport and single-user model

### NFR-04: Python Stack

- Language: **Python 3.12+**
- Package manager: **UV**
- MCP framework: **FastMCP**
- ORM/DB layer: **SQLAlchemy 2.x** (async) + **asyncpg** driver + **Alembic** migrations
- Validation: **Pydantic v2** (FastMCP uses it natively)
- Testing: **pytest** + **pytest-asyncio** + **Hypothesis** (PBT, partial mode)

### NFR-05: Docker

- **Production image**: minimal Python image, UV-installed dependencies, pinned base image tag (no `latest`)
- **Dev compose**: `docker-compose.dev.yml` with hot-reload (Watchfiles or equivalent) and PostgreSQL service
- **Production compose**: `docker-compose.yml` with PostgreSQL service and MCP server
- Lock file (`uv.lock`) MUST be committed and used in Docker builds

### NFR-06: Logging

- Structured JSON logging (stdlib `logging` + `python-json-logger` or equivalent)
- Every log entry MUST include: `timestamp`, `level`, `message`, and `request context` where applicable
- Sensitive data (no PII, no DB credentials) MUST NOT appear in logs
- Log output to stdout (container-friendly)

---

## Extension Configuration

| Extension | Enabled | Mode | Decided At |
|---|---|---|---|
| Security Baseline | Yes | Full (all 15 rules blocking) | Requirements Analysis |
| Property-Based Testing | Yes | Partial (PBT-02, PBT-03, PBT-07, PBT-08, PBT-09 enforced; others advisory) | Requirements Analysis |

### Security Rules — Applicability Notes

| Rule | Status | Note |
|---|---|---|
| SECURITY-01 | Applicable | PostgreSQL encryption at rest + TLS for DB connection |
| SECURITY-02 | N/A | No load balancer or API gateway (stdio transport) |
| SECURITY-03 | Applicable | Structured logging required |
| SECURITY-04 | N/A | No HTML endpoints (MCP stdio, not HTTP) |
| SECURITY-05 | Applicable | Input validation on all MCP tool parameters |
| SECURITY-06 | N/A | No IAM policies (no cloud infra) |
| SECURITY-07 | Applicable (scoped) | Docker network must restrict Postgres port to internal only |
| SECURITY-08 | N/A | Single-user stdio transport — no network auth layer |
| SECURITY-09 | Applicable | No default creds, no stack traces in errors, pinned Docker tags |
| SECURITY-10 | Applicable | uv.lock committed, pinned Docker base image, vulnerability scanning in CI |
| SECURITY-11 | Applicable (scoped) | Input validation + error handling as defense layers; rate limiting N/A (stdio) |
| SECURITY-12 | N/A | No user authentication system |
| SECURITY-13 | Applicable | Safe deserialization (Pydantic), no unsafe eval |
| SECURITY-14 | Applicable (scoped) | Log retention and alerting advisory; structured logs required |
| SECURITY-15 | Applicable | Fail-closed error handling, global exception handler, resource cleanup |

---

## Key Constraints and Decisions

1. **stdio + Postgres**: The MCP server runs as a subprocess (stdio) but connects to a Postgres container. These are independent — Claude Desktop spawns the server process, which then connects to the DB via `DATABASE_URL`.
2. **Subtasks are one level deep**: Subtasks are stored as a JSONB column or a child table with a foreign key — they do not have their own subtasks.
3. **Soft delete is the only delete**: There is no permanent delete tool exposed. Soft-deleted items are preserved and restorable.
4. **No HTTP transport**: FastMCP supports both stdio and HTTP/SSE, but only stdio is configured. The server is not exposed as a standalone HTTP service.
