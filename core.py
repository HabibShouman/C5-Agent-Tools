"""Application logic, separate from MCP transport. Author: Habib Shouman."""
from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Text = Annotated[str, Field(min_length=1, max_length=120)]
RequestID = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")]
Minutes = Annotated[int, Field(ge=15, le=240, strict=True)]


class Space(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    space_id: str
    name: str
    quiet: bool
    seats: int
    provenance: str = "Fictional teaching catalogue; not live availability"


class SavedSession(BaseModel):
    session_id: int
    request_id: str
    title: str
    location: str
    minutes: int
    created: bool
    effect: str = "Local study-session record only; no room reservation"


class Plan(BaseModel):
    space: Space
    session: SavedSession
    steps: list[str]


class DomainError(ValueError):
    """Expected application failure safe to return to a caller."""


CATALOGUE = {
    "quiet-1": Space(space_id="quiet-1", name="Cedar Quiet Room", quiet=True, seats=12),
    "group-1": Space(space_id="group-1", name="Olive Group Room", quiet=False, seats=6),
    "quiet-2": Space(space_id="quiet-2", name="Pine Reading Corner", quiet=True, seats=4),
}


def nonblank(value: str, label: str) -> str:
    value = value.strip()
    if not value or len(value) > 120:
        raise DomainError(f"INVALID_INPUT: {label} must contain 1 to 120 nonblank characters.")
    return value


class StudyService:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def lookup_space(self, space_id: str) -> Space:
        """Read only: never creates a database or changes the catalogue."""
        try:
            return CATALOGUE[space_id]
        except KeyError as exc:
            raise DomainError("SPACE_NOT_FOUND: use quiet-1, group-1, or quiet-2.") from exc

    def save_session(self, title: str, location: str, minutes: int, request_id: str) -> SavedSession:
        # Validate even when called without the MCP/Pydantic boundary.
        title = nonblank(title, "title")
        location = nonblank(location, "location")
        import re
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", request_id):
            raise DomainError("INVALID_INPUT: request_id must be 1-64 letters, digits, '_' or '-'.")
        if type(minutes) is not int or not 15 <= minutes <= 240:
            raise DomainError("INVALID_INPUT: minutes must be an integer from 15 to 240.")
        payload = json.dumps([title, location, minutes], ensure_ascii=False)
        fingerprint = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with closing(sqlite3.connect(self.db_path, timeout=5)) as db:
                with db:
                    db.execute("CREATE TABLE IF NOT EXISTS sessions ("
                               "session_id INTEGER PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, "
                               "fingerprint TEXT NOT NULL, title TEXT NOT NULL, "
                               "location TEXT NOT NULL, minutes INTEGER NOT NULL)")
                    # INSERT OR IGNORE plus the unique key makes concurrent retries safe.
                    cursor = db.execute(
                        "INSERT OR IGNORE INTO sessions "
                        "(request_id,fingerprint,title,location,minutes) VALUES (?,?,?,?,?)",
                        (request_id, fingerprint, title, location, minutes),
                    )
                    created = cursor.rowcount == 1
                    row = db.execute("SELECT session_id,fingerprint,title,location,minutes "
                                     "FROM sessions WHERE request_id=?", (request_id,)).fetchone()
                    if row is None:
                        raise DomainError("STORAGE_ERROR: no session was returned; retry with the same request_id.")
                    if row[1] != fingerprint:
                        raise DomainError("IDEMPOTENCY_CONFLICT: request_id already belongs to a different payload; "
                                          "use a new ID for a genuinely new session.")
                    return SavedSession(session_id=row[0], request_id=request_id, title=row[2],
                                        location=row[3], minutes=row[4], created=created)
        except (sqlite3.Error, OSError) as exc:
            raise DomainError("STORAGE_ERROR: could not save the local session; check the configured "
                              "database path and permissions, then retry with the same request_id.") from exc

    def plan_session(self, space_id: str, title: str, minutes: int, request_id: str) -> Plan:
        # These are the same two service methods exposed by the Data and Action tools.
        # No nested MCP connection and no duplicate implementation of either operation.
        log = logging.getLogger("study")
        log.info("STEP lookup_space")
        space = self.lookup_space(space_id)
        log.info("STEP save_study_session")
        session = self.save_session(title, space.name, minutes, request_id)
        return Plan(space=space, session=session, steps=["lookup_space", "save_study_session"])
