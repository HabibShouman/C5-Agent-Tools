"""Real subprocess/stdio tests using the Agents SDK MCP client, without a model."""
import json
import sqlite3

from host import make_server


def payload(result):
    if result.structured_content:
        return result.structured_content
    return json.loads(next(c.text for c in result.content if c.type == "text"))


async def test_three_tools_and_roundtrips(tmp_path):
    path = tmp_path / "wire.db"
    async with make_server(str(path)) as server:
        tools = await server.list_tools()
        assert {t.name for t in tools} == {"lookup_space", "save_study_session", "plan_study_session"}
        for tool in tools:
            assert tool.description and tool.input_schema["type"] == "object"
            assert tool.output_schema
        data = await server.call_tool("lookup_space", {"space_id": "quiet-1"})
        assert not data.is_error and payload(data)["quiet"] is True
        assert not path.exists()
        bad = await server.call_tool("lookup_space", {"space_id": "missing"})
        assert bad.is_error and "SPACE_NOT_FOUND" in str(bad.content)
        action_args = {"title": "MCP", "location": "Home", "minutes": 30, "request_id": "wire-action"}
        saved = await server.call_tool("save_study_session", action_args)
        assert not saved.is_error and payload(saved)["created"] is True
        retry = await server.call_tool("save_study_session", action_args)
        assert payload(retry)["created"] is False
        conflict = await server.call_tool("save_study_session", {**action_args, "title": "Changed"})
        assert conflict.is_error and "IDEMPOTENCY_CONFLICT" in str(conflict.content)
        invalid = await server.call_tool("save_study_session", {**action_args, "minutes": 0})
        assert invalid.is_error
        plan_args = {"space_id": "group-1", "title": "Agents", "minutes": 60, "request_id": "wire-plan"}
        plan = await server.call_tool("plan_study_session", plan_args)
        assert not plan.is_error
        assert payload(plan)["session"]["location"] == "Olive Group Room"
        bad_plan = await server.call_tool("plan_study_session", {**plan_args, "space_id": "missing", "request_id": "bad"})
        assert bad_plan.is_error and "SPACE_NOT_FOUND" in str(bad_plan.content)
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 2
