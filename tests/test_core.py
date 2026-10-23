from concurrent.futures import ThreadPoolExecutor
import sqlite3

import pytest

from core import DomainError, StudyService


def rows(path):
    with sqlite3.connect(path) as db:
        return db.execute("SELECT title,location,minutes FROM sessions").fetchall()


def test_data_has_no_write(tmp_path):
    path = tmp_path / "study.db"
    s = StudyService(path)
    room = s.lookup_space("quiet-1")
    assert room.name == "Cedar Quiet Room" and room.quiet and room.seats == 12
    assert not path.exists()


def test_unknown_space_has_no_effect(tmp_path):
    path = tmp_path / "study.db"
    with pytest.raises(DomainError, match="SPACE_NOT_FOUND"):
        StudyService(path).plan_session("missing", "ML", 60, "bad-space")
    assert not path.exists()


def test_action_persists_across_instances(tmp_path):
    path = tmp_path / "study.db"
    first = StudyService(path).save_session("  ML  ", "Home", 60, "one")
    second = StudyService(path).save_session("ML", "Home", 60, "one")
    assert first.created and not second.created
    assert first.session_id == second.session_id
    assert rows(path) == [("ML", "Home", 60)]


def test_conflicting_retry_preserves_original(tmp_path):
    path = tmp_path / "study.db"
    s = StudyService(path)
    s.save_session("ML", "Home", 60, "one")
    with pytest.raises(DomainError, match="IDEMPOTENCY_CONFLICT"):
        s.save_session("Different", "Home", 60, "one")
    assert rows(path) == [("ML", "Home", 60)]


@pytest.mark.parametrize("minutes", [14, 241, True, 60.5, "60"])
def test_bad_duration_no_write(tmp_path, minutes):
    path = tmp_path / "study.db"
    with pytest.raises(DomainError, match="INVALID_INPUT"):
        StudyService(path).save_session("ML", "Home", minutes, "one")
    assert not path.exists()


@pytest.mark.parametrize("minutes", [15, 240])
def test_duration_boundaries(tmp_path, minutes):
    assert StudyService(tmp_path / "study.db").save_session("ML", "Home", minutes, "one").minutes == minutes


def test_blank_title_and_unsafe_id(tmp_path):
    s = StudyService(tmp_path / "study.db")
    with pytest.raises(DomainError, match="INVALID_INPUT"):
        s.save_session("   ", "Home", 60, "one")
    with pytest.raises(DomainError, match="INVALID_INPUT"):
        s.save_session("ML", "Home", 60, "../path")


def test_storage_failure(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("not a directory")
    with pytest.raises(DomainError, match="STORAGE_ERROR"):
        StudyService(blocker / "study.db").save_session("ML", "Home", 60, "one")


def test_orchestration_order_and_values(tmp_path, monkeypatch):
    s = StudyService(tmp_path / "study.db")
    events = []
    lookup, save = s.lookup_space, s.save_session
    def observed_lookup(*args):
        events.append("lookup")
        return lookup(*args)
    def observed_save(*args):
        events.append("save")
        return save(*args)
    monkeypatch.setattr(s, "lookup_space", observed_lookup)
    monkeypatch.setattr(s, "save_session", observed_save)
    plan = s.plan_session("group-1", "Agents", 90, "plan")
    assert events == ["lookup", "save"]
    assert plan.session.location == "Olive Group Room"
    assert rows(s.db_path) == [("Agents", "Olive Group Room", 90)]


def test_concurrent_identical_retries(tmp_path):
    path = tmp_path / "study.db"
    def write(_):
        return StudyService(path).save_session("ML", "Home", 60, "concurrent")
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(write, range(8)))
    assert sum(r.created for r in results) == 1
    assert len({r.session_id for r in results}) == 1
    assert len(rows(path)) == 1
