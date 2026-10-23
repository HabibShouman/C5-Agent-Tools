"""Read-only inspection of persisted effects, outside the MCP tool surface."""
import argparse
import json
import sqlite3
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--db", default="study.db")
args = parser.parse_args()
path = Path(args.db).resolve()
if not path.is_file():
    raise SystemExit("No database yet; no saved sessions to inspect.")
with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    rows = db.execute("SELECT session_id,request_id,title,location,minutes FROM sessions ORDER BY session_id").fetchall()
    print(json.dumps([dict(row) for row in rows], indent=2, ensure_ascii=False))
