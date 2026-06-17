# Domain Entities — Unit 1: Data Layer

## Entity: Todo

The central domain object. Represents a single task in the todo list.

### Fields

| Field | Type | Required | Constraints |
|---|---|---|---|
| `id` | UUID v4 | Yes | Auto-generated on creation; immutable |
| `title` | string | Yes | Max 255 characters; non-empty |
| `description` | string | Yes | May be empty string; no max length |
| `status` | Status enum | Yes | One of: `to_do`, `in_progress`, `blocked`, `done` |
| `priority` | Priority enum | Yes | One of: `high`, `medium`, `low` |
| `due_date` | date (ISO 8601) | Yes | Valid calendar date |
| `created_at` | datetime (UTC) | Yes | Auto-set on creation; immutable |
| `updated_at` | datetime (UTC) | Yes | Auto-updated on every mutation |
| `deleted_at` | datetime (UTC) | No | Null = active; non-null = soft-deleted |
| `project` | string | No | Max 255 characters; null if not set |
| `tags` | string[] | No | Default empty list; each tag max 100 chars; **case-sensitive** |
| `assignee` | string | No | Max 255 characters; null if not set |
| `effort` | string | No | Free-text (e.g. "30 minutes"); max 100 chars; null if not set |
| `subtasks` | Subtask[] | No | Default empty list; one level only — subtasks have no children |

### State Lifecycle

```
created (deleted_at=null)
    │
    │ delete_todo
    ▼
soft-deleted (deleted_at=<timestamp>)
    │
    │ restore_todo
    ▼
active again (deleted_at=null)
```

- A todo can be soft-deleted and restored any number of times.
- Status transitions (`to_do` → `in_progress` → `blocked` → `done`) are free — any status can be set from any other status via `update_todo`. No enforced state machine.

---

## Entity: Subtask

A child task belonging to exactly one parent Todo. Cannot have its own subtasks.

### Fields

| Field | Type | Required | Constraints |
|---|---|---|---|
| `id` | UUID v4 | Yes | Auto-generated on creation; immutable |
| `todo_id` | UUID v4 | Yes | FK → Todo.id; ON DELETE CASCADE |
| `title` | string | Yes | Max 255 characters; non-empty |
| `done` | boolean | Yes | Default `false` |

### Rules
- Subtasks are always loaded with their parent Todo (no lazy loading).
- When a Todo is hard-deleted from the DB (cascade), its subtasks are also deleted.
- When `update_todo` passes a `subtasks` list, the update is a **merge/upsert**:
  - Subtasks with an existing `id` in the list are updated (title and/or done flag).
  - Subtasks in the list with no `id` (or a new UUID) are inserted.
  - Subtasks currently on the Todo but **not present** in the provided list are **left unchanged**.

---

## Enums

### Status
| Value | Meaning |
|---|---|
| `to_do` | Not started |
| `in_progress` | Actively being worked on |
| `blocked` | Cannot proceed — waiting on something |
| `done` | Completed |

### Priority
| Value | Meaning |
|---|---|
| `high` | Urgent / most important |
| `medium` | Normal importance |
| `low` | Can wait |

### SortField
`created_at` | `updated_at` | `due_date` | `priority` | `title`

**Priority sort order** (ascending): `high` → `medium` → `low`
**Priority sort order** (descending): `low` → `medium` → `high`

### SortOrder
`asc` | `desc` — default `asc`

---

## Entity Relationships

```
Todo (1) ──────────── (0..*) Subtask
         FK: subtask.todo_id → todo.id
         ON DELETE CASCADE
```

No other entity relationships. Tags, project, and assignee are plain string fields — no separate entity tables.
