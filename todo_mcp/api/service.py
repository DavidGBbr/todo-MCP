import math
from uuid import UUID

from todo_mcp.core.schemas import (
    CreateTodoInput,
    ListTodosInput,
    ListTodosOut,
    TodoOut,
    UpdateTodoInput,
)
from todo_mcp.db.models import Todo
from todo_mcp.db.repository import TodoRepository


class TodoService:
    def __init__(self, repo: TodoRepository) -> None:
        self._repo = repo

    async def create_todo(self, data: CreateTodoInput) -> TodoOut:
        todo = await self._repo.create(data)
        return _to_todo_out(todo)

    async def get_todo(self, todo_id: UUID) -> TodoOut:
        todo = await self._repo.get_by_id(todo_id)
        return _to_todo_out(todo)

    async def update_todo(self, todo_id: UUID, data: UpdateTodoInput) -> TodoOut:
        todo = await self._repo.update(todo_id, data)
        return _to_todo_out(todo)

    async def delete_todo(self, todo_id: UUID) -> TodoOut:
        todo = await self._repo.soft_delete(todo_id)
        return _to_todo_out(todo)

    async def restore_todo(self, todo_id: UUID) -> TodoOut:
        todo = await self._repo.restore(todo_id)
        return _to_todo_out(todo)

    async def list_todos(self, filters: ListTodosInput) -> ListTodosOut:
        todos, total = await self._repo.list(filters)
        total_pages = math.ceil(total / filters.page_size) if total > 0 else 0
        return ListTodosOut(
            items=[_to_todo_out(todo) for todo in todos],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
        )


def _to_todo_out(todo: Todo) -> TodoOut:
    return TodoOut.model_validate(todo)
