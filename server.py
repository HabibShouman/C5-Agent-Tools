"""FastMCP stdio server: exactly three callable tools. Author: Habib Shouman."""
import logging
import os
from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from core import DomainError, Minutes, Plan, RequestID, SavedSession, Space, StudyService, Text

logging.basicConfig(level=logging.INFO, format="SERVER %(message)s")  # stderr, never stdout
log = logging.getLogger("study")
mcp = FastMCP("Campus Study Toolkit", mask_error_details=True)
service = StudyService(Path(os.environ.get("STUDY_DB", str(Path(__file__).parent / "study.db"))))


def execute(name, operation, *args):
    log.info("START %s", name)
    try:
        result = operation(*args)
    except DomainError as exc:
        log.info("ERROR %s %s", name, str(exc).split(":", 1)[0])
        raise ToolError(str(exc)) from exc
    log.info("END %s", name)
    return result


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
def lookup_space(space_id: Annotated[str, Field(description="Catalogue ID: quiet-1, group-1, or quiet-2")]) -> Space:
    """Data: retrieve one fictional campus study space. No writes or live availability claims.
    Unknown IDs raise SPACE_NOT_FOUND. Choose this for information-only questions.
    """
    return execute("lookup_space", service.lookup_space, space_id)


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False,
                       "idempotentHint": True, "openWorldHint": False})
def save_study_session(
    title: Annotated[Text, Field(description="Study topic or session title")],
    location: Annotated[Text, Field(description="User-supplied location name; need not be a catalogue space")],
    minutes: Annotated[Minutes, Field(description="Planned study duration, 15-240 minutes; not a booking")],
    request_id: Annotated[RequestID, Field(description="Unique ID per intended session; reuse exactly for retries")],
) -> SavedSession:
    """Action: persist one local study-session record. No room reservation or notification.
    Use only when the user requests saving. Same ID and payload returns the existing row;
    changed payload raises IDEMPOTENCY_CONFLICT. Invalid input or storage failures are errors.
    """
    return execute("save_study_session", service.save_session, title, location, minutes, request_id)


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False,
                       "idempotentHint": True, "openWorldHint": False})
def plan_study_session(
    space_id: Annotated[str, Field(description="Catalogue ID: quiet-1, group-1, or quiet-2")],
    title: Annotated[Text, Field(description="Study topic or session title")],
    minutes: Annotated[Minutes, Field(description="Planned study duration, 15-240 minutes")],
    request_id: Annotated[RequestID, Field(description="Unique ID per intended session; reuse for retries")],
) -> Plan:
    """Orchestration: create a local study plan at a catalogue space by calling lookup then save.
    Use for a request to look up a catalogue space and save a session there. Stops without
    saving on unknown space. Inherits action validation, storage and duplicate-ID errors.
    This creates a personal record, never reserves the space.
    """
    return execute("plan_study_session", service.plan_session, space_id, title, minutes, request_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
