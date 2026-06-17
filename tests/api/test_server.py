import pytest

from todo_mcp.api.server import create_mcp_server


@pytest.mark.asyncio
async def test_server_registers_all_tools() -> None:
    mcp = create_mcp_server()

    tools = await mcp.list_tools()
    names = {tool.name for tool in tools}

    assert names == {
        "create_todo",
        "get_todo",
        "update_todo",
        "delete_todo",
        "restore_todo",
        "list_todos",
    }
