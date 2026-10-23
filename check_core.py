"""Dependency-light executable checks: Python + Pydantic only; no MCP/model claim."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest
from unittest.mock import patch

from core import DomainError, StudyService


class CoreChecks(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "study.db"
        self.service = StudyService(self.path)

    def count(self):
        with sqlite3.connect(self.path) as db:
            return db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]

    def test_read_only(self):
        room = self.service.lookup_space("quiet-1")
        self.assertEqual((room.name, room.quiet, room.seats), ("Cedar Quiet Room", True, 12))
        self.assertFalse(self.path.exists())

    def test_unknown_space_stops_before_write(self):
        with patch.object(self.service, "save_session", wraps=self.service.save_session) as save:
            with self.assertRaisesRegex(DomainError, "SPACE_NOT_FOUND"):
                self.service.plan_session("unknown", "MCP", 60, "no-write")
            save.assert_not_called()
        self.assertFalse(self.path.exists())

    def test_persistence_and_duplicate(self):
        a = self.service.save_session("MCP", "Home", 60, "one")
        b = StudyService(self.path).save_session("MCP", "Home", 60, "one")
        self.assertTrue(a.created)
        self.assertFalse(b.created)
        self.assertEqual(a.session_id, b.session_id)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute("SELECT title,location,minutes FROM sessions").fetchall(),
                             [("MCP", "Home", 60)])

    def test_conflict_preserves_original(self):
        self.service.save_session("MCP", "Home", 60, "one")
        with self.assertRaisesRegex(DomainError, "IDEMPOTENCY_CONFLICT"):
            self.service.save_session("Other", "Home", 60, "one")
        self.assertEqual(self.count(), 1)

    def test_invalid_inputs_no_write(self):
        for minutes in [14, 241, True, 60.5, "60"]:
            with self.subTest(minutes=minutes), self.assertRaisesRegex(DomainError, "INVALID_INPUT"):
                self.service.save_session("MCP", "Home", minutes, "one")
        for title, location, request_id in [(" ", "Home", "one"), ("MCP", " ", "one"),
                                             ("MCP", "Home", "../escape")]:
            with self.subTest(title=title, location=location, request_id=request_id):
                with self.assertRaisesRegex(DomainError, "INVALID_INPUT"):
                    self.service.save_session(title, location, 60, request_id)
        self.assertFalse(self.path.exists())

    def test_boundary_durations(self):
        for minutes in (15, 240):
            result = self.service.save_session("MCP", "Home", minutes, str(minutes))
            self.assertEqual(result.minutes, minutes)
        self.assertEqual(self.count(), 2)

    def test_storage_error(self):
        blocker = Path(self.temp.name) / "blocker"
        blocker.write_text("file, not directory")
        with self.assertRaisesRegex(DomainError, "STORAGE_ERROR"):
            StudyService(blocker / "study.db").save_session("MCP", "Home", 60, "one")

    def test_orchestration_sequence(self):
        events = []
        lookup, save = self.service.lookup_space, self.service.save_session
        def watched_lookup(*args):
            events.append("read")
            return lookup(*args)
        def watched_save(*args):
            events.append("write")
            return save(*args)
        with patch.object(self.service, "lookup_space", side_effect=watched_lookup), \
             patch.object(self.service, "save_session", side_effect=watched_save):
            result = self.service.plan_session("group-1", "Agents", 90, "plan")
        self.assertEqual(events, ["read", "write"])
        self.assertEqual(result.session.location, "Olive Group Room")
        self.assertEqual(self.count(), 1)

    def test_concurrent_retries(self):
        def write(_):
            return StudyService(self.path).save_session("MCP", "Home", 60, "same")
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(write, range(8)))
        self.assertEqual(sum(r.created for r in results), 1)
        self.assertEqual(len({r.session_id for r in results}), 1)
        self.assertEqual(self.count(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
