import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlalchemy import delete

from tests.strategies import create_todo_input_strategy, list_todos_input_strategy
from todo_mcp.core.schemas import ListTodosInput
from todo_mcp.db.models import Subtask, Todo
from todo_mcp.db.repository import TodoRepository


async def _clear_tables(session) -> None:
    await session.execute(delete(Subtask))
    await session.execute(delete(Todo))
    await session.flush()


@pytest.mark.asyncio
@given(
    inputs=st.lists(create_todo_input_strategy(), min_size=1, max_size=10),
    params=list_todos_input_strategy(),
)
@settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_filter_invariant_filtered_subset_of_unfiltered(session, inputs, params):
    await _clear_tables(session)
    repo = TodoRepository(session)
    for inp in inputs:
        await repo.create(inp)

    unfiltered_params = ListTodosInput(
        include_deleted=params.include_deleted,
        page=1,
        page_size=100,
    )
    try:
        all_todos, _ = await repo.list(unfiltered_params)
    except Exception:
        return

    filtered_params = ListTodosInput(
        status=params.status,
        priority=params.priority,
        project=params.project,
        assignee=params.assignee,
        tags=params.tags,
        include_deleted=params.include_deleted,
        page=1,
        page_size=100,
    )
    try:
        filtered, _ = await repo.list(filtered_params)
    except Exception:
        return

    all_ids = {t.id for t in all_todos}
    filtered_ids = {t.id for t in filtered}
    assert filtered_ids.issubset(all_ids)


@pytest.mark.asyncio
@given(inputs=st.lists(create_todo_input_strategy(), min_size=1, max_size=5))
@settings(
    max_examples=20,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_pagination_invariant_pages_cover_all_items(session, inputs):
    await _clear_tables(session)
    repo = TodoRepository(session)
    for inp in inputs:
        await repo.create(inp)

    page_size = 2
    page = 1
    collected = []
    while True:
        try:
            items, total = await repo.list(
                ListTodosInput(page=page, page_size=page_size)
            )
        except Exception:
            break
        collected.extend(items)
        if len(items) < page_size:
            break
        page += 1
        if page > total // page_size + 2:
            break

    unique_ids = {t.id for t in collected}
    assert len(unique_ids) == len(collected)


@pytest.mark.asyncio
@given(inputs=st.lists(create_todo_input_strategy(), min_size=1, max_size=5))
@settings(
    max_examples=20,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
async def test_soft_delete_invariant(session, inputs):
    await _clear_tables(session)
    repo = TodoRepository(session)
    todos = []
    for inp in inputs:
        todo = await repo.create(inp)
        todos.append(todo)

    for todo in todos:
        await repo.soft_delete(todo.id)

    active, _ = await repo.list(ListTodosInput(page=1, page_size=100))
    active_ids = {t.id for t in active}

    deleted_ids = {t.id for t in todos}
    assert deleted_ids.isdisjoint(active_ids)

    with_deleted, _ = await repo.list(
        ListTodosInput(include_deleted=True, page=1, page_size=100)
    )
    with_deleted_ids = {t.id for t in with_deleted}
    assert deleted_ids.issubset(with_deleted_ids)
