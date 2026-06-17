import math
import uuid
from datetime import datetime, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from todo_mcp.core.enums import Priority, SortField, SortOrder
from todo_mcp.core.exceptions import (
    PageOutOfRangeError,
    TodoAlreadyDeletedError,
    TodoNotDeletedError,
    TodoNotFoundError,
)
from todo_mcp.core.schemas import CreateTodoInput, ListTodosInput, UpdateTodoInput
from todo_mcp.db.models import Subtask, Todo

_PRIORITY_ORDER = {Priority.high: 0, Priority.medium: 1, Priority.low: 2}


class TodoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: CreateTodoInput) -> Todo:
        todo = Todo(
            id=uuid.uuid4(),
            title=data.title,
            description=data.description,
            status=data.status.value,
            priority=data.priority.value,
            due_date=data.due_date,
            project=data.project,
            tags=data.tags,
            assignee=data.assignee,
            effort=data.effort,
        )
        now = datetime.now(timezone.utc)
        todo.created_at = now
        todo.updated_at = now

        for sub in data.subtasks:
            todo.subtasks.append(
                Subtask(
                    id=uuid.uuid4(),
                    title=sub.title,
                    done=sub.done,
                )
            )

        self._session.add(todo)
        await self._session.flush()
        await self._session.refresh(todo)
        return todo

    async def get_by_id(self, todo_id: uuid.UUID) -> Todo:
        stmt = select(Todo).where(Todo.id == todo_id)
        result = await self._session.execute(stmt)
        todo = result.scalar_one_or_none()
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return todo

    async def update(self, todo_id: uuid.UUID, data: UpdateTodoInput) -> Todo:
        todo = await self.get_by_id(todo_id)

        if data.title is not None:
            todo.title = data.title
        if data.description is not None:
            todo.description = data.description
        if data.status is not None:
            todo.status = data.status.value
        if data.priority is not None:
            todo.priority = data.priority.value
        if data.due_date is not None:
            todo.due_date = data.due_date
        if data.project is not None:
            todo.project = data.project
        if data.tags is not None:
            todo.tags = data.tags
        if data.assignee is not None:
            todo.assignee = data.assignee
        if data.effort is not None:
            todo.effort = data.effort

        if data.subtasks is not None:
            existing = {sub.id: sub for sub in todo.subtasks}
            for sub_input in data.subtasks:
                if sub_input.id is not None and sub_input.id in existing:
                    existing[sub_input.id].title = sub_input.title
                    existing[sub_input.id].done = sub_input.done
                else:
                    todo.subtasks.append(
                        Subtask(
                            id=uuid.uuid4(),
                            title=sub_input.title,
                            done=sub_input.done,
                        )
                    )

        todo.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._session.refresh(todo)
        return todo

    async def soft_delete(self, todo_id: uuid.UUID) -> Todo:
        todo = await self.get_by_id(todo_id)
        if todo.deleted_at is not None:
            raise TodoAlreadyDeletedError(todo_id)
        now = datetime.now(timezone.utc)
        todo.deleted_at = now
        todo.updated_at = now
        await self._session.flush()
        return todo

    async def restore(self, todo_id: uuid.UUID) -> Todo:
        todo = await self.get_by_id(todo_id)
        if todo.deleted_at is None:
            raise TodoNotDeletedError(todo_id)
        todo.deleted_at = None
        todo.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        return todo

    async def list(self, params: ListTodosInput) -> tuple[list[Todo], int]:
        stmt = select(Todo)

        if not params.include_deleted:
            stmt = stmt.where(Todo.deleted_at.is_(None))

        if params.status is not None:
            stmt = stmt.where(Todo.status == params.status.value)
        if params.priority is not None:
            stmt = stmt.where(Todo.priority == params.priority.value)
        if params.project is not None:
            stmt = stmt.where(Todo.project == params.project)
        if params.assignee is not None:
            stmt = stmt.where(Todo.assignee == params.assignee)
        if params.tags is not None:
            stmt = stmt.where(Todo.tags.op("&&")(params.tags))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        total_pages = max(1, math.ceil(total / params.page_size)) if total > 0 else 0

        if total > 0 and params.page > total_pages:
            raise PageOutOfRangeError(params.page, params.page_size, total_pages)

        sort_col = _resolve_sort_column(params.sort_by, params.sort_order)
        stmt = stmt.order_by(sort_col)
        stmt = stmt.limit(params.page_size).offset((params.page - 1) * params.page_size)

        result = await self._session.execute(stmt)
        todos = list(result.scalars().all())
        return todos, total


def _resolve_sort_column(sort_by: SortField, sort_order: SortOrder):  # type: ignore[no-untyped-def]
    asc = sort_order == SortOrder.asc

    if sort_by == SortField.priority:
        priority_case = case(
            (Todo.priority == Priority.high.value, 0),
            (Todo.priority == Priority.medium.value, 1),
            (Todo.priority == Priority.low.value, 2),
            else_=3,
        )
        return priority_case.asc() if asc else priority_case.desc()

    col = getattr(Todo, sort_by.value)
    return col.asc() if asc else col.desc()
