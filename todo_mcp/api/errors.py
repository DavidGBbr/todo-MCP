import json
import logging
from typing import Any

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from todo_mcp.core.exceptions import (
    PageOutOfRangeError,
    TodoAlreadyDeletedError,
    TodoNotDeletedError,
    TodoNotFoundError,
)

logger = logging.getLogger(__name__)


class InvalidToolInputError(Exception):
    def __init__(self, message: str, code: str = "INVALID_INPUT") -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def make_mcp_error(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def error_payload_for_exception(exc: Exception) -> dict[str, str]:
    if isinstance(exc, TodoNotFoundError):
        return make_mcp_error("TODO_NOT_FOUND", f"Todo {exc.todo_id} not found")
    if isinstance(exc, TodoAlreadyDeletedError):
        return make_mcp_error(
            "TODO_ALREADY_DELETED", f"Todo {exc.todo_id} is already deleted"
        )
    if isinstance(exc, TodoNotDeletedError):
        return make_mcp_error("TODO_NOT_DELETED", f"Todo {exc.todo_id} is not deleted")
    if isinstance(exc, PageOutOfRangeError):
        return make_mcp_error(
            "PAGE_OUT_OF_RANGE",
            f"Page {exc.page} is out of range; total pages: {exc.total_pages}",
        )
    if isinstance(exc, InvalidToolInputError):
        return make_mcp_error(exc.code, exc.message)
    if isinstance(exc, ValidationError):
        return make_mcp_error("VALIDATION_ERROR", "Invalid tool input")

    logger.exception("Unhandled MCP tool error")
    return make_mcp_error("INTERNAL_ERROR", "An unexpected error occurred")


def to_tool_error(exc: Exception) -> ToolError:
    payload: dict[str, Any] = error_payload_for_exception(exc)
    return ToolError(json.dumps(payload, separators=(",", ":")))
