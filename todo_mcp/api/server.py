import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from fastmcp import FastMCP

from todo_mcp.api.tools import register_tools
from todo_mcp.core.config import get_settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"))


def setup_logging() -> None:
    settings = get_settings()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())


def create_mcp_server() -> FastMCP:
    mcp = FastMCP(
        "todo-mcp",
        instructions="Manage a PostgreSQL-backed todo list over MCP stdio.",
        mask_error_details=True,
        strict_input_validation=True,
    )
    register_tools(mcp)
    return mcp


mcp = create_mcp_server()


def main() -> None:
    setup_logging()
    mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
