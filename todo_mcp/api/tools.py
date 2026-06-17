from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from functools import wraps
from uuid import UUID

from fastmcp.exceptions import ToolError
from sqlalchemy.ext.asyncio import AsyncSession

from todo_mcp.api.errors import InvalidToolInputError, to_tool_error
from todo_mcp.api.service import TodoService
from todo_mcp.core.schemas import (
    CreateTodoInput,
    ListTodosInput,
    ListTodosOut,
    TodoOut,
    UpdateTodoInput,
)
from todo_mcp.db.repository import TodoRepository

SessionContextFactory = Callable[[], AbstractAsyncContextManager[AsyncSession]]

_session_context_factory: SessionContextFactory | None = None


def set_session_context_factory(factory: SessionContextFactory | None) -> None:
    global _session_context_factory
    _session_context_factory = factory


@asynccontextmanager
async def _default_session_context() -> AsyncIterator[AsyncSession]:
    from todo_mcp.db.database import get_session

    async with get_session() as session:
        yield session


def _session_context() -> AbstractAsyncContextManager[AsyncSession]:
    if _session_context_factory is not None:
        return _session_context_factory()
    return _default_session_context()


def handle_tool_errors[**P, R](
    fn: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    @wraps(fn)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await fn(*args, **kwargs)
        except ToolError:
            raise
        except Exception as exc:
            raise to_tool_error(exc) from exc

    return wrapper


async def _with_service[R](operation: Callable[[TodoService], Awaitable[R]]) -> R:
    async with _session_context() as session:
        service = TodoService(TodoRepository(session))
        return await operation(service)


def _parse_uuid(value: str) -> UUID:
    try:
        todo_id = UUID(value)
    except ValueError as exc:
        raise InvalidToolInputError("todo_id must be a valid UUID v4") from exc

    if todo_id.version != 4:
        raise InvalidToolInputError("todo_id must be a valid UUID v4")
    return todo_id


@handle_tool_errors
async def create_todo(input: CreateTodoInput) -> TodoOut:
    return await _with_service(lambda service: service.create_todo(input))


@handle_tool_errors
async def get_todo(todo_id: str) -> TodoOut:
    parsed_id = _parse_uuid(todo_id)
    return await _with_service(lambda service: service.get_todo(parsed_id))


@handle_tool_errors
async def update_todo(todo_id: str, input: UpdateTodoInput) -> TodoOut:
    parsed_id = _parse_uuid(todo_id)
    return await _with_service(lambda service: service.update_todo(parsed_id, input))


@handle_tool_errors
async def delete_todo(todo_id: str) -> TodoOut:
    parsed_id = _parse_uuid(todo_id)
    return await _with_service(lambda service: service.delete_todo(parsed_id))


@handle_tool_errors
async def restore_todo(todo_id: str) -> TodoOut:
    parsed_id = _parse_uuid(todo_id)
    return await _with_service(lambda service: service.restore_todo(parsed_id))


@handle_tool_errors
async def list_todos(input: ListTodosInput) -> ListTodosOut:
    return await _with_service(lambda service: service.list_todos(input))


def register_tools(mcp: object) -> None:
    tool_registrar = getattr(mcp, "tool")
    tool_registrar()(create_todo)
    tool_registrar()(get_todo)
    tool_registrar()(update_todo)
    tool_registrar()(delete_todo)
    tool_registrar()(restore_todo)
    tool_registrar()(list_todos)
