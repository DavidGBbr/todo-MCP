import uuid
from datetime import date

import pytest

from todo_mcp.core.exceptions import (
    PageOutOfRangeError,
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
from todo_mcp.db.repository import TodoRepository


def _make_input(**kwargs) -> CreateTodoInput:
    defaults = dict(
        title="Test todo",
        description="A description",
        status="to_do",
        priority="medium",
        due_date=date(2030, 1, 1),
    )
    defaults.update(kwargs)
    return CreateTodoInput(**defaults)


@pytest.mark.asyncio
async def test_create_and_get(session):
    repo = TodoRepository(session)
    todo = await repo.create(_make_input(title="Hello", tags=["work", "urgent"]))
    fetched = await repo.get_by_id(todo.id)
    assert fetched.title == "Hello"
    assert fetched.tags == ["work", "urgent"]


@pytest.mark.asyncio
async def test_create_with_subtasks(session):
    repo = TodoRepository(session)
    inp = _make_input(
        subtasks=[
            SubtaskInput(title="Sub A", done=False),
            SubtaskInput(title="Sub B", done=True),
        ]
    )
    todo = await repo.create(inp)
    assert len(todo.subtasks) == 2
    titles = {s.title for s in todo.subtasks}
    assert titles == {"Sub A", "Sub B"}


@pytest.mark.asyncio
async def test_get_not_found(session):
    repo = TodoRepository(session)
    with pytest.raises(TodoNotFoundError):
        await repo.get_by_id(uuid.uuid4())


@pytest.mark.asyncio
async def test_update_title(session):
    repo = TodoRepository(session)
    todo = await repo.create(_make_input())
    updated = await repo.update(todo.id, UpdateTodoInput(title="Updated title"))
    assert updated.title == "Updated title"


@pytest.mark.asyncio
async def test_update_status(session):
    repo = TodoRepository(session)
    todo = await repo.create(_make_input())
    updated = await repo.update(todo.id, UpdateTodoInput(status="done"))
    assert updated.status == "done"


@pytest.mark.asyncio
async def test_update_subtask_upsert(session):
    repo = TodoRepository(session)
    todo = await repo.create(
        _make_input(subtasks=[SubtaskInput(title="Original", done=False)])
    )
    existing_id = todo.subtasks[0].id

    updated = await repo.update(
        todo.id,
        UpdateTodoInput(
            subtasks=[
                SubtaskInput(id=existing_id, title="Modified", done=True),
                SubtaskInput(title="New sub", done=False),
            ]
        ),
    )
    by_id = {s.id: s for s in updated.subtasks}
    assert by_id[existing_id].title == "Modified"
    assert by_id[existing_id].done is True
    assert len(updated.subtasks) == 2


@pytest.mark.asyncio
async def test_update_subtasks_absent_leaves_unchanged(session):
    repo = TodoRepository(session)
    todo = await repo.create(
        _make_input(subtasks=[SubtaskInput(title="Keep me", done=False)])
    )
    updated = await repo.update(todo.id, UpdateTodoInput(title="New title"))
    assert len(updated.subtasks) == 1
    assert updated.subtasks[0].title == "Keep me"


@pytest.mark.asyncio
async def test_soft_delete(session):
    repo = TodoRepository(session)
    todo = await repo.create(_make_input())
    deleted = await repo.soft_delete(todo.id)
    assert deleted.deleted_at is not None


@pytest.mark.asyncio
async def test_soft_delete_already_deleted(session):
    repo = TodoRepository(session)
    todo = await repo.create(_make_input())
    await repo.soft_delete(todo.id)
    with pytest.raises(TodoAlreadyDeletedError):
        await repo.soft_delete(todo.id)


@pytest.mark.asyncio
async def test_restore(session):
    repo = TodoRepository(session)
    todo = await repo.create(_make_input())
    await repo.soft_delete(todo.id)
    restored = await repo.restore(todo.id)
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_restore_not_deleted(session):
    repo = TodoRepository(session)
    todo = await repo.create(_make_input())
    with pytest.raises(TodoNotDeletedError):
        await repo.restore(todo.id)


@pytest.mark.asyncio
async def test_list_returns_active_only_by_default(session):
    repo = TodoRepository(session)
    todo1 = await repo.create(_make_input(title="Active"))
    todo2 = await repo.create(_make_input(title="Deleted"))
    await repo.soft_delete(todo2.id)

    todos, total = await repo.list(ListTodosInput())
    ids = {t.id for t in todos}
    assert todo1.id in ids
    assert todo2.id not in ids


@pytest.mark.asyncio
async def test_list_include_deleted(session):
    repo = TodoRepository(session)
    todo = await repo.create(_make_input(title="Will be deleted"))
    await repo.soft_delete(todo.id)

    todos, total = await repo.list(ListTodosInput(include_deleted=True))
    ids = {t.id for t in todos}
    assert todo.id in ids


@pytest.mark.asyncio
async def test_list_filter_by_status(session):
    repo = TodoRepository(session)
    await repo.create(_make_input(title="Todo item", status="to_do"))
    await repo.create(_make_input(title="Done item", status="done"))

    todos, _ = await repo.list(ListTodosInput(status="to_do"))
    assert all(t.status == "to_do" for t in todos)


@pytest.mark.asyncio
async def test_list_filter_by_priority(session):
    repo = TodoRepository(session)
    await repo.create(_make_input(title="High prio", priority="high"))
    await repo.create(_make_input(title="Low prio", priority="low"))

    todos, _ = await repo.list(ListTodosInput(priority="high"))
    assert all(t.priority == "high" for t in todos)


@pytest.mark.asyncio
async def test_list_pagination(session):
    repo = TodoRepository(session)
    for i in range(5):
        await repo.create(_make_input(title=f"Item {i}"))

    page1, total = await repo.list(ListTodosInput(page=1, page_size=2))
    assert len(page1) <= 2
    assert total >= 5


@pytest.mark.asyncio
async def test_list_page_out_of_range(session):
    repo = TodoRepository(session)
    await repo.create(_make_input())

    with pytest.raises(PageOutOfRangeError):
        await repo.list(ListTodosInput(page=999, page_size=100))


@pytest.mark.asyncio
async def test_list_empty_page_one_ok(session):
    repo = TodoRepository(session)
    # Ensure at least this session has no active items (fresh session with rollback)
    todos, total = await repo.list(ListTodosInput())
    assert isinstance(todos, list)
