import pytest
from hypothesis import given, settings

from tests.strategies import todo_out_strategy
from todo_mcp.core.schemas import (
    CreateTodoInput,
    ListTodosInput,
    SubtaskInput,
    TodoOut,
    UpdateTodoInput,
)


# --- Example-based: CreateTodoInput ---


def test_create_todo_valid():
    data = CreateTodoInput(
        title="Buy groceries",
        description="Milk and eggs",
        status="to_do",
        priority="high",
        due_date="2030-01-01",
    )
    assert data.title == "Buy groceries"
    assert data.tags == []
    assert data.subtasks == []


def test_create_todo_title_empty_rejected():
    with pytest.raises(Exception):
        CreateTodoInput(
            title="",
            description="",
            status="to_do",
            priority="high",
            due_date="2030-01-01",
        )


def test_create_todo_title_too_long_rejected():
    with pytest.raises(Exception):
        CreateTodoInput(
            title="x" * 256,
            description="",
            status="to_do",
            priority="high",
            due_date="2030-01-01",
        )


def test_create_todo_invalid_status_rejected():
    with pytest.raises(Exception):
        CreateTodoInput(
            title="Test",
            description="",
            status="flying",
            priority="high",
            due_date="2030-01-01",
        )


def test_create_todo_invalid_priority_rejected():
    with pytest.raises(Exception):
        CreateTodoInput(
            title="Test",
            description="",
            status="to_do",
            priority="critical",
            due_date="2030-01-01",
        )


def test_create_todo_invalid_due_date_rejected():
    with pytest.raises(Exception):
        CreateTodoInput(
            title="Test",
            description="",
            status="to_do",
            priority="high",
            due_date="not-a-date",
        )


def test_tag_max_length_enforced():
    with pytest.raises(Exception):
        CreateTodoInput(
            title="Test",
            description="",
            status="to_do",
            priority="high",
            due_date="2030-01-01",
            tags=["x" * 101],
        )


def test_effort_max_length_enforced():
    with pytest.raises(Exception):
        CreateTodoInput(
            title="Test",
            description="",
            status="to_do",
            priority="high",
            due_date="2030-01-01",
            effort="x" * 101,
        )


# --- Example-based: UpdateTodoInput ---


def test_update_todo_all_none_valid():
    data = UpdateTodoInput()
    assert data.title is None
    assert data.status is None


def test_update_todo_invalid_status_rejected():
    with pytest.raises(Exception):
        UpdateTodoInput(status="invalid_status")


# --- Example-based: ListTodosInput ---


def test_list_todos_defaults():
    data = ListTodosInput()
    assert data.page == 1
    assert data.page_size == 20
    assert not data.include_deleted


def test_list_todos_page_zero_rejected():
    with pytest.raises(Exception):
        ListTodosInput(page=0)


def test_list_todos_page_size_zero_rejected():
    with pytest.raises(Exception):
        ListTodosInput(page_size=0)


def test_list_todos_page_size_over_100_rejected():
    with pytest.raises(Exception):
        ListTodosInput(page_size=101)


# --- Example-based: SubtaskInput ---


def test_subtask_title_empty_rejected():
    with pytest.raises(Exception):
        SubtaskInput(title="")


def test_subtask_title_too_long_rejected():
    with pytest.raises(Exception):
        SubtaskInput(title="x" * 256)


# --- PBT-02: TodoOut round-trip ---


@given(todo_out_strategy())
@settings(max_examples=100)
def test_todo_out_round_trip(todo: TodoOut):
    dumped = todo.model_dump()
    restored = TodoOut.model_validate(dumped)
    assert restored == todo
