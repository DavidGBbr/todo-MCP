# Component Methods — todo-mcp

Detailed business rules are defined in Functional Design (Construction phase). This document covers method signatures, input/output types, and high-level purpose.

---

## `core/config.py`

```python
class Settings(BaseSettings):
    database_url: PostgresDsn
    log_level: str = "INFO"
    db_pool_size: int = 5
    db_max_overflow: int = 10

def get_settings() -> Settings: ...
# Returns a cached Settings singleton; reads from environment variables
```

---

## `core/schemas.py`

### Input schemas (MCP tool arguments)

```python
class CreateTodoInput(BaseModel):
    title: str                        # max 255 chars
    description: str
    status: Status
    priority: Priority
    due_date: date
    project: str | None = None
    tags: list[str] = []
    assignee: str | None = None
    effort: str | None = None
    subtasks: list[SubtaskInput] = []

class SubtaskInput(BaseModel):
    title: str                        # max 255 chars

class UpdateTodoInput(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Status | None = None
    priority: Priority | None = None
    due_date: date | None = None
    project: str | None = None
    tags: list[str] | None = None
    assignee: str | None = None
    effort: str | None = None
    subtasks: list[SubtaskInput] | None = None

class ListTodosInput(BaseModel):
    status: list[Status] | None = None
    priority: list[Priority] | None = None
    project: str | None = None
    tags: list[str] | None = None
    assignee: str | None = None
    due_before: date | None = None
    due_after: date | None = None
    include_deleted: bool = False
    sort_by: SortField = SortField.created_at
    sort_order: SortOrder = SortOrder.asc
    page: int = 1                     # 1-based
    page_size: int = 20               # max 100
```

### Output schemas (MCP tool responses)

```python
class SubtaskOut(BaseModel):
    id: UUID
    title: str
    done: bool

class TodoOut(BaseModel):
    id: UUID
    title: str
    description: str
    status: Status
    priority: Priority
    due_date: date
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    project: str | None
    tags: list[str]
    assignee: str | None
    effort: str | None
    subtasks: list[SubtaskOut]

class ListTodosOut(BaseModel):
    items: list[TodoOut]
    total: int
    page: int
    page_size: int
    total_pages: int
```

---

## `db/models.py`

```python
class Todo(Base):
    __tablename__ = "todos"

    id: UUID                  # PK, default uuid4
    title: str
    description: str
    status: str               # maps to Status enum
    priority: str             # maps to Priority enum
    due_date: date
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    project: str | None
    tags: list[str]           # ARRAY(Text)
    assignee: str | None
    effort: str | None
    subtasks: list[Subtask]   # relationship

class Subtask(Base):
    __tablename__ = "subtasks"

    id: UUID                  # PK, default uuid4
    todo_id: UUID             # FK → todos.id, ON DELETE CASCADE
    title: str
    done: bool                # default False
```

---

## `db/database.py`

```python
async def create_engine(settings: Settings) -> AsyncEngine: ...
# Creates asyncpg-backed engine with pool_size and max_overflow

async def get_session() -> AsyncGenerator[AsyncSession, None]: ...
# Async context manager; yields a session, commits on success, rolls back on error
```

---

## `db/repository.py`

```python
class TodoRepository:
    def __init__(self, session: AsyncSession) -> None: ...

    async def create(self, data: CreateTodoInput) -> Todo: ...
    # Inserts todo + subtasks in one transaction; returns ORM object

    async def get_by_id(self, todo_id: UUID) -> Todo | None: ...
    # Fetches by PK; returns None if not found (includes soft-deleted)

    async def update(self, todo_id: UUID, data: UpdateTodoInput) -> Todo | None: ...
    # Applies partial update; sets updated_at; returns updated object or None

    async def soft_delete(self, todo_id: UUID) -> Todo | None: ...
    # Sets deleted_at = now(); returns updated object or None if not found

    async def restore(self, todo_id: UUID) -> Todo | None: ...
    # Clears deleted_at; returns updated object or None

    async def list(self, filters: ListTodosInput) -> tuple[list[Todo], int]: ...
    # Returns (items_for_page, total_count) applying all filters/sort/pagination
```

---

## `api/service.py`

```python
class TodoService:
    def __init__(self, repo: TodoRepository) -> None: ...

    async def create_todo(self, data: CreateTodoInput) -> TodoOut: ...
    async def get_todo(self, todo_id: UUID) -> TodoOut: ...
    # Raises NotFoundError if not found

    async def update_todo(self, todo_id: UUID, data: UpdateTodoInput) -> TodoOut: ...
    # Raises NotFoundError; enforces subtask one-level constraint

    async def delete_todo(self, todo_id: UUID) -> TodoOut: ...
    # Soft-delete; raises NotFoundError; raises AlreadyDeletedError if already deleted

    async def restore_todo(self, todo_id: UUID) -> TodoOut: ...
    # Raises NotFoundError; raises NotDeletedError if not currently deleted

    async def list_todos(self, filters: ListTodosInput) -> ListTodosOut: ...
    # Assembles filter params, delegates to repo, paginates, returns typed output
```

---

## `api/tools.py`

```python
# Each function is a thin FastMCP tool handler:

@mcp.tool()
async def create_todo(input: CreateTodoInput) -> TodoOut: ...

@mcp.tool()
async def get_todo(todo_id: str) -> TodoOut: ...

@mcp.tool()
async def update_todo(todo_id: str, input: UpdateTodoInput) -> TodoOut: ...

@mcp.tool()
async def delete_todo(todo_id: str) -> TodoOut: ...

@mcp.tool()
async def restore_todo(todo_id: str) -> TodoOut: ...

@mcp.tool()
async def list_todos(input: ListTodosInput) -> ListTodosOut: ...
```

---

## `api/errors.py`

```python
class TodoNotFoundError(Exception):
    todo_id: UUID

class TodoAlreadyDeletedError(Exception):
    todo_id: UUID

class TodoNotDeletedError(Exception):
    todo_id: UUID

class ValidationError(Exception):
    code: str
    message: str

def make_mcp_error(code: str, message: str) -> dict: ...
# Returns structured {"code": ..., "message": ...} safe for MCP response

# Global error handler registered on FastMCP app:
# Catches all unhandled exceptions → logs with logger → returns make_mcp_error("INTERNAL_ERROR", "An unexpected error occurred")
```
