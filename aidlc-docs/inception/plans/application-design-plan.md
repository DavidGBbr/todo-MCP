# Application Design Plan — todo-mcp

## Plan Checkboxes

- [x] Answer design questions below
- [x] Generate components.md
- [x] Generate component-methods.md
- [x] Generate services.md
- [x] Generate component-dependency.md
- [x] Generate application-design.md (consolidated)
- [x] Validate design completeness

---

## Design Questions

Please fill in the letter choice after each `[Answer]:` tag, then let me know when done.

---

### Question 1
Should there be an explicit **service layer** between the MCP tool handlers and the database repositories, or should tool handlers call repositories directly?

A) **Direct** — MCP tool handlers call the repository directly (simpler, fewer layers, fine for a minimal server)
B) **Service layer** — a `TodoService` class sits between tools and repository, owning business logic (soft-delete, filter assembly, subtask handling); tools stay thin
X) Other (please describe after [Answer]: tag below)

[Answer]: Option B

---

### Question 2
What **package layout** should the project use?

A) **Flat** — all modules in one top-level package: `todo_mcp/models.py`, `todo_mcp/repository.py`, `todo_mcp/server.py`, etc.
B) **Layered** — subpackages by concern: `todo_mcp/db/` (models + migrations), `todo_mcp/api/` (tools), `todo_mcp/core/` (schemas + config)
X) Other (please describe after [Answer]: tag below)

[Answer]: option B

---

### Question 3
How should **configuration** (DATABASE_URL, log level, etc.) be managed?

A) `pydantic-settings` — a `Settings` class reads from environment variables with type validation and defaults
B) Plain `os.environ` / `os.getenv` — simple direct reads at startup, no extra dependency
X) Other (please describe after [Answer]: tag below)

[Answer]: option A

---

### Question 4
Should **subtasks** be stored as a **JSONB column** on the todo row, or in a **separate child table** with a foreign key back to the parent todo?

A) JSONB column on the todo row (simpler schema, no join needed, subtasks always loaded with parent)
B) Separate `subtasks` table with FK to `todos` (more relational, easier to query/index individually)
X) Other (please describe after [Answer]: tag below)

[Answer]: option B
