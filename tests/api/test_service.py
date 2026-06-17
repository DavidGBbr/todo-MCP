import uuid
from datetime import UTC, date, datetime
from types import SimpleNamespace

import pytest

from todo_mcp.api.service import TodoService
from todo_mcp.core.exceptions import (
    TodoAlreadyDeletedError,
    TodoNotDeletedError,
    TodoNotFoundError,
)
from todo_mcp.core.schemas import (
    CreateTodoInput,
    ListTodosInput,
    SubtaskInput,
    UpdateTodoInput,
)


def _todo(**overrides):
    now = datetime.now(UTC)
    data = dict(
        id=uuid.uuid4(),
        title="Test todo",
        description="Description",
        status="to_do",
        priority="medium",
        due_date=date(2030, 1, 1),
        created_at=now,
        updated_at=now,
        deleted_at=None,
        project=None,
        tags=[],
        assignee=None,
        effort=None,
        subtasks=[],
    )
    data.update(overrides)
    return SimpleNamespace(**data)


class FakeRepo:
    def __init__(self) -> None:
        self.todo = _todo()

    async def create(self, data: CreateTodoInput):
        self.todo = _todo(
            title=data.title,
            description=data.description,
            status=data.status.value,
            priority=data.priority.value,
            due_date=data.due_date,
            subtasks=[
                SimpleNamespace(
                    id=uuid.uuid4(),
                    todo_id=self.todo.id,
                    title=sub.title,
                    done=sub.done,
                )
                for sub in data.subtasks
            ],
        )
        return self.todo

    async def get_by_id(self, todo_id: uuid.UUID):
        if todo_id != self.todo.id:
            raise TodoNotFoundError(todo_id)
        return self.todo

    async def update(self, todo_id: uuid.UUID, data: UpdateTodoInput):
        await self.get_by_id(todo_id)
        if data.title is not None:
            self.todo.title = data.title
        return self.todo

    async def soft_delete(self, todo_id: uuid.UUID):
        await self.get_by_id(todo_id)
        if self.todo.deleted_at is not None:
            raise TodoAlreadyDeletedError(todo_id)
        self.todo.deleted_at = datetime.now(UTC)
        return self.todo

    async def restore(self, todo_id: uuid.UUID):
        await self.get_by_id(todo_id)
        if self.todo.deleted_at is None:
            raise TodoNotDeletedError(todo_id)
        self.todo.deleted_at = None
        return self.todo

    async def list(self, filters: ListTodosInput):
        return [self.todo], 1


@pytest.mark.asyncio
async def test_service_create_maps_repository_model_to_schema() -> None:
    repo = FakeRepo()
    service = TodoService(repo)  # type: ignore[arg-type]

    result = await service.create_todo(
        CreateTodoInput(
            title="Write tests",
            description="Cover service",
            status="to_do",
            priority="high",
            due_date=date(2030, 1, 1),
            subtasks=[SubtaskInput(title="First")],
        )
    )

    assert result.title == "Write tests"
    assert result.priority == "high"
    assert result.subtasks[0].title == "First"


@pytest.mark.asyncio
async def test_service_delete_restore_guards_are_preserved() -> None:
    repo = FakeRepo()
    service = TodoService(repo)  # type: ignore[arg-type]

    deleted = await service.delete_todo(repo.todo.id)
    assert deleted.deleted_at is not None

    with pytest.raises(TodoAlreadyDeletedError):
        await service.delete_todo(repo.todo.id)

    restored = await service.restore_todo(repo.todo.id)
    assert restored.deleted_at is None

    with pytest.raises(TodoNotDeletedError):
        await service.restore_todo(repo.todo.id)


@pytest.mark.asyncio
async def test_service_list_computes_total_pages() -> None:
    repo = FakeRepo()
    service = TodoService(repo)  # type: ignore[arg-type]

    result = await service.list_todos(ListTodosInput(page_size=20))

    assert result.total == 1
    assert result.total_pages == 1
    assert result.items[0].id == repo.todo.id
