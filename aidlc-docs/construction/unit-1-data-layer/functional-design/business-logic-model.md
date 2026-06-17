# Business Logic Model — Unit 1: Data Layer

## Overview

Unit 1 owns all data persistence logic. It has no MCP or transport concerns — it only knows about domain objects, validation, and database operations.

---

## Operation: create_todo

```
Input: CreateTodoInput
Output: TodoOut
Errors: VALIDATION_ERROR

1. Validate all required fields present and non-null (BR-01)
2. Validate field lengths (BR-02)
3. Validate status and priority enum values (BR-03)
4. Validate due_date format (BR-05)
5. Validate each tag length ≤ 100 chars (BR-02)
6. Generate id = UUID v4
7. Set created_at = updated_at = now() UTC
8. Set deleted_at = null
9. For each subtask in input.subtasks:
   a. Validate subtask.title non-empty and ≤ 255 chars (BR-02)
   b. Generate subtask.id = UUID v4 (BR-16)
   c. Set subtask.done = false
10. INSERT todo row + subtask rows in single transaction
11. Return TodoOut mapped from inserted rows
```

---

## Operation: get_todo

```
Input: todo_id (UUID string)
Output: TodoOut (includes soft-deleted items)
Errors: VALIDATION_ERROR, TODO_NOT_FOUND

1. Validate todo_id is valid UUID v4 (BR-04)
2. SELECT todo + subtasks WHERE id = todo_id (no deleted_at filter)
3. If not found → raise TODO_NOT_FOUND (BR-08)
4. Return TodoOut (deleted_at may be populated)
```

---

## Operation: update_todo

```
Input: todo_id (UUID string), UpdateTodoInput (all fields optional)
Output: TodoOut
Errors: VALIDATION_ERROR, TODO_NOT_FOUND

1. Validate todo_id is valid UUID v4 (BR-04)
2. SELECT existing todo; if not found → raise TODO_NOT_FOUND (BR-08)
3. For each provided field, validate:
   - title: ≤ 255 chars, non-empty if provided (BR-02)
   - status: valid enum value (BR-03)
   - priority: valid enum value (BR-03)
   - due_date: valid ISO 8601 date (BR-05)
   - project/assignee: ≤ 255 chars (BR-02)
   - effort: ≤ 100 chars (BR-02)
   - tags: each value ≤ 100 chars (BR-02)
4. If subtasks list is provided, apply merge (BR-10):
   a. For each subtask in list with an id matching an existing subtask:
      → UPDATE that subtask's title and/or done flag
   b. For each subtask in list with no matching existing id:
      → INSERT as new subtask (generate UUID, set done=false) (BR-16)
   c. Existing subtasks not in list → leave unchanged
5. Apply all validated scalar changes to todo row
6. Set updated_at = now() UTC (BR-15)
7. COMMIT
8. Return TodoOut
```

---

## Operation: delete_todo (soft)

```
Input: todo_id (UUID string)
Output: TodoOut
Errors: VALIDATION_ERROR, TODO_NOT_FOUND, TODO_ALREADY_DELETED

1. Validate todo_id is valid UUID v4 (BR-04)
2. SELECT todo; if not found → raise TODO_NOT_FOUND (BR-08)
3. If deleted_at IS NOT NULL → raise TODO_ALREADY_DELETED (BR-06)
4. SET deleted_at = now() UTC, updated_at = now() UTC (BR-15)
5. COMMIT
6. Return TodoOut (deleted_at now populated)
```

---

## Operation: restore_todo

```
Input: todo_id (UUID string)
Output: TodoOut
Errors: VALIDATION_ERROR, TODO_NOT_FOUND, TODO_NOT_DELETED

1. Validate todo_id is valid UUID v4 (BR-04)
2. SELECT todo; if not found → raise TODO_NOT_FOUND (BR-08)
3. If deleted_at IS NULL → raise TODO_NOT_DELETED (BR-07)
4. SET deleted_at = NULL, updated_at = now() UTC (BR-15)
5. COMMIT
6. Return TodoOut (deleted_at now null)
```

---

## Operation: list_todos

```
Input: ListTodosInput (all fields optional)
Output: ListTodosOut
Errors: VALIDATION_ERROR, PAGE_OUT_OF_RANGE

1. Validate page ≥ 1 (BR-13)
2. Validate page_size between 1 and 100 (BR-13)
3. Build WHERE clause:
   a. Unless include_deleted=true: WHERE deleted_at IS NULL (BR-14)
   b. If status filter: WHERE status IN (...)
   c. If priority filter: WHERE priority IN (...)
   d. If project filter: WHERE project = :project  [exact match]
   e. If tags filter: WHERE tags && ARRAY[:tags]  [any-of, case-sensitive] (BR-11)
   f. If assignee filter: WHERE assignee = :assignee  [exact match]
   g. If due_before: WHERE due_date <= :due_before
   h. If due_after: WHERE due_date >= :due_after
4. Build ORDER BY clause from sort_by + sort_order:
   - priority sort: use CASE expression mapping high=1, medium=2, low=3
5. Execute COUNT(*) query with WHERE clause → total
6. Compute total_pages = ceil(total / page_size); if total=0 → total_pages=0
7. If page > total_pages AND total > 0 → raise PAGE_OUT_OF_RANGE (BR-12)
8. Execute SELECT with WHERE + ORDER BY + LIMIT page_size OFFSET (page-1)*page_size
9. Return ListTodosOut { items, total, page, page_size, total_pages }
```

---

## PBT Property Identification (PBT-01)

Properties identified for Hypothesis testing in the test suite:

| Property | Category | Description |
|---|---|---|
| Schema round-trip | Round-trip | `TodoOut.model_validate(todo_out.model_dump())` equals original for any generated `TodoOut` |
| Filter invariant | Invariant | Filtered list is always a subset of unfiltered list; count(filtered) ≤ count(unfiltered) |
| Pagination invariant | Invariant | Sum of items across all pages equals `total`; no item appears on two pages |
| Soft-delete invariant | Invariant | `list_todos()` never returns items with `deleted_at != null` unless `include_deleted=true` |
| Subtask merge idempotency | Idempotency | Applying the same subtask upsert list twice yields the same state as once |

These are carried forward as requirements for the test suite in Code Generation.
