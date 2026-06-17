import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date

import pytest
from fastmcp.exceptions import ToolError
from sqlalchemy.ext.asyncio import AsyncSession

from todo_mcp.api import tools
from todo_mcp.core.schemas import CreateTodoInput, ListTodosInput, UpdateTodoInput


@asynccontextmanager
async def _session_context(session: AsyncSession) -> AsyncIterator[AsyncSession]:
    yield session


@pytest.fixture(autouse=True)
def reset_session_context_factory():
    yield
    tools.set_session_context_factory(None)


def _make_input(**overrides) -> CreateTodoInput:
    data = dict(
        title="Tool todo",
        description="Created by tool",
        status="to_do",
        priority="medium",
        due_date=date(2030, 1, 1),
    )
    data.update(overrides)
    return CreateTodoInput(**data)


@pytest.mark.asyncio
async def test_tool_create_get_update_list_delete_restore_cycle(
    session: AsyncSession,
) -> None:
    tools.set_session_context_factory(lambda: _session_context(session))

    created = await tools.create_todo(_make_input(title="Created"))
    fetched = await tools.get_todo(str(created.id))
    updated = await tools.update_todo(str(created.id), UpdateTodoInput(title="Updated"))
    listed = await tools.list_todos(ListTodosInput(status="to_do", page_size=10))
    deleted = await tools.delete_todo(str(created.id))
    restored = await tools.restore_todo(str(created.id))

    assert fetched.id == created.id
    assert updated.title == "Updated"
    assert created.id in {todo.id for todo in listed.items}
    assert deleted.deleted_at is not None
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_tool_invalid_uuid_returns_structured_error(
    session: AsyncSession,
) -> None:
    tools.set_session_context_factory(lambda: _session_context(session))

    with pytest.raises(ToolError) as exc_info:
        await tools.get_todo("not-a-uuid")

    payload = json.loads(str(exc_info.value))
    assert payload == {
        "code": "INVALID_INPUT",
        "message": "todo_id must be a valid UUID v4",
    }
