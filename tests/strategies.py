from datetime import date, timedelta
from uuid import uuid4

from hypothesis import strategies as st

from todo_mcp.core.enums import Priority, SortField, SortOrder, Status
from todo_mcp.core.schemas import CreateTodoInput, ListTodosInput, SubtaskInput, TodoOut, SubtaskOut

_statuses = st.sampled_from(list(Status))
_priorities = st.sampled_from(list(Priority))
_sort_fields = st.sampled_from(list(SortField))
_sort_orders = st.sampled_from(list(SortOrder))

_tag = st.text(min_size=1, max_size=100).filter(lambda s: s.strip())
_tags = st.lists(_tag, max_size=5)
_title = st.text(min_size=1, max_size=255).filter(lambda s: s.strip())
_opt_str_255 = st.one_of(st.none(), st.text(min_size=1, max_size=255).filter(lambda s: s.strip()))
_opt_str_100 = st.one_of(st.none(), st.text(min_size=1, max_size=100).filter(lambda s: s.strip()))

_today = date.today()
_due_date = st.dates(min_value=_today, max_value=_today + timedelta(days=365 * 5))


def subtask_input_strategy() -> st.SearchStrategy[SubtaskInput]:
    return st.builds(
        SubtaskInput,
        id=st.none(),
        title=_title,
        done=st.booleans(),
    )


def create_todo_input_strategy() -> st.SearchStrategy[CreateTodoInput]:
    return st.builds(
        CreateTodoInput,
        title=_title,
        description=st.text(max_size=2000),
        status=_statuses,
        priority=_priorities,
        due_date=_due_date,
        project=_opt_str_255,
        tags=_tags,
        assignee=_opt_str_255,
        effort=_opt_str_100,
        subtasks=st.lists(subtask_input_strategy(), max_size=5),
    )


def list_todos_input_strategy() -> st.SearchStrategy[ListTodosInput]:
    return st.builds(
        ListTodosInput,
        status=st.one_of(st.none(), _statuses),
        priority=st.one_of(st.none(), _priorities),
        project=st.one_of(st.none(), st.text(min_size=1, max_size=255)),
        assignee=st.one_of(st.none(), st.text(min_size=1, max_size=255)),
        tags=st.one_of(st.none(), _tags),
        include_deleted=st.booleans(),
        sort_by=_sort_fields,
        sort_order=_sort_orders,
        page=st.integers(min_value=1, max_value=10),
        page_size=st.integers(min_value=1, max_value=100),
    )


def subtask_out_strategy() -> st.SearchStrategy[SubtaskOut]:
    return st.builds(
        SubtaskOut,
        id=st.uuids(),
        todo_id=st.uuids(),
        title=_title,
        done=st.booleans(),
    )


def todo_out_strategy() -> st.SearchStrategy[TodoOut]:
    _datetime = st.datetimes(timezones=st.just(__import__("datetime").timezone.utc))
    return st.builds(
        TodoOut,
        id=st.uuids(),
        title=_title,
        description=st.text(max_size=2000),
        status=_statuses,
        priority=_priorities,
        due_date=_due_date,
        created_at=_datetime,
        updated_at=_datetime,
        deleted_at=st.one_of(st.none(), _datetime),
        project=_opt_str_255,
        tags=_tags,
        assignee=_opt_str_255,
        effort=_opt_str_100,
        subtasks=st.lists(subtask_out_strategy(), max_size=5),
    )
