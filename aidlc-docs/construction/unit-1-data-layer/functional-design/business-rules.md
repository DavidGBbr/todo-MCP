# Business Rules — Unit 1: Data Layer

## BR-01: Required Field Validation

**Rule**: On `create_todo`, all required fields must be present and non-null. Missing or null required fields are rejected before any DB write.

**Fields**: `title`, `description`, `status`, `priority`, `due_date`

**Violation response**: Structured error `VALIDATION_ERROR` with a message identifying which field(s) failed.

---

## BR-02: Field Length Constraints

**Rule**: String fields must not exceed their maximum length.

| Field | Max length |
|---|---|
| `title` (Todo) | 255 chars |
| `title` (Subtask) | 255 chars |
| `project` | 255 chars |
| `assignee` | 255 chars |
| `effort` | 100 chars |
| Each tag value | 100 chars |

**Violation response**: `VALIDATION_ERROR` identifying the field and constraint.

---

## BR-03: Enum Validation

**Rule**: `status` and `priority` must be one of the defined enum values. Any other value is rejected.

- Valid `status`: `to_do`, `in_progress`, `blocked`, `done`
- Valid `priority`: `high`, `medium`, `low`

**Violation response**: `VALIDATION_ERROR` with the invalid value and the list of valid options.

---

## BR-04: UUID Format Validation

**Rule**: Any field or argument that accepts a UUID (e.g. `todo_id`, `subtask.id` on update) must be a valid UUID v4 string. Malformed UUIDs are rejected before any DB query.

**Violation response**: `VALIDATION_ERROR` with the field name and value.

---

## BR-05: Due Date Validation

**Rule**: `due_date` must parse as a valid ISO 8601 calendar date (`YYYY-MM-DD`). Invalid date strings (e.g. `"2024-13-01"`, `"not-a-date"`) are rejected.

**Violation response**: `VALIDATION_ERROR` identifying `due_date`.

---

## BR-06: Soft Delete Guard

**Rule**: `delete_todo` may only be applied to a Todo that is currently **active** (`deleted_at IS NULL`). Attempting to delete an already-deleted Todo raises an error.

**Violation response**: `TODO_ALREADY_DELETED` with the `todo_id`.

---

## BR-07: Restore Guard

**Rule**: `restore_todo` may only be applied to a Todo that is currently **soft-deleted** (`deleted_at IS NOT NULL`). Attempting to restore an active Todo raises an error.

**Violation response**: `TODO_NOT_DELETED` with the `todo_id`.

---

## BR-08: Not Found

**Rule**: Any operation that references a `todo_id` that does not exist in the database raises a not-found error. This applies to `get_todo`, `update_todo`, `delete_todo`, and `restore_todo`.

**Violation response**: `TODO_NOT_FOUND` with the `todo_id`.

---

## BR-09: Subtask One-Level Depth

**Rule**: Subtasks are a flat list on a Todo. Subtasks cannot have their own subtasks. The data model enforces this by having no self-referencing FK on the `subtasks` table. The service layer must reject any input that attempts nested subtask creation.

---

## BR-10: Subtask Update Strategy (Merge/Upsert)

**Rule**: When `update_todo` includes a `subtasks` list, the update is a **merge**:

1. For each subtask in the provided list **with a matching existing `id`**: update its `title` and/or `done` flag.
2. For each subtask in the provided list **with no existing `id`** (or a new UUID not in the DB): insert as a new subtask.
3. Subtasks currently attached to the Todo but **absent from the provided list**: **leave unchanged**.

To remove a subtask, it must be explicitly deleted via a dedicated subtask-delete mechanism (not yet a separate tool in this version — subtask removal is deferred to a future tool). For now, passing a subtasks list in `update_todo` cannot delete existing subtasks.

---

## BR-11: Tag Case Sensitivity

**Rule**: Tags are **case-sensitive**. `@Computer` and `@computer` are treated as distinct tag values. Tags are stored exactly as provided and compared exactly on filter. No normalisation is applied on write or read.

---

## BR-12: Pagination Out-of-Range

**Rule**: If the requested `page` number exceeds the computed `total_pages`, the server returns a structured error.

**Violation response**: `PAGE_OUT_OF_RANGE` with `page`, `page_size`, and `total_pages` in the error detail.

**Exception**: If `total` is 0, `total_pages` is 0. A request for `page=1` with 0 results is valid — returns empty `items` (not an error), since page 1 is always the first page.

---

## BR-13: Pagination Constraints

**Rule**: `page_size` must be between 1 and 100 (inclusive). `page` must be ≥ 1.

**Violation response**: `VALIDATION_ERROR` identifying the field and constraint.

---

## BR-14: list_todos Default Behaviour

**Rule**: By default, `list_todos` returns only **active** todos (`deleted_at IS NULL`). Soft-deleted items are only included when `include_deleted=true` is explicitly passed.

---

## BR-15: updated_at Auto-Update

**Rule**: Every mutation (`update_todo`, `delete_todo`, `restore_todo`) must set `updated_at` to the current UTC timestamp. `created_at` is never modified after creation.

---

## BR-16: Subtask Auto-ID on Create

**Rule**: When a new subtask is added (via `create_todo` or `update_todo` merge), its `id` is auto-generated as UUID v4 by the server. The caller does not supply subtask IDs for new subtasks.

**Note**: On `update_todo` merge, the caller may supply an existing subtask `id` to update that subtask. If the supplied `id` does not match any existing subtask on that Todo, it is treated as a new subtask insert.

---

## Error Code Reference

| Code | Trigger |
|---|---|
| `VALIDATION_ERROR` | BR-01, BR-02, BR-03, BR-04, BR-05, BR-13 |
| `TODO_NOT_FOUND` | BR-08 |
| `TODO_ALREADY_DELETED` | BR-06 |
| `TODO_NOT_DELETED` | BR-07 |
| `PAGE_OUT_OF_RANGE` | BR-12 |
| `INTERNAL_ERROR` | Any unhandled exception (global handler) |
