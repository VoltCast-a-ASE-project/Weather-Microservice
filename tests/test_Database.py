import pytest
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock
from app.Database import Database
from app.models.geocode import SimpleLocation

# Test data
TEST_LOCATION = SimpleLocation(name="Test Place", lat=12.34, lon=56.78)
USERNAME = "alice"


@pytest.fixture
def db_instance():
    # Create a temp file and close it immediately so SQLite can open it
    tmpfile = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmpfile.close()
    db = Database(tmpfile.name)
    db.setup_db()  # create tables
    yield db


def test_setup_db_creates_tables(db_instance):
    # Should not raise any exception
    db_instance.setup_db()

    # Verify tables exist
    with db_instance.connect() as con:
        cur = con.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
    assert "users" in tables
    assert "locations" in tables


def test_save_and_get_location(db_instance):
    db_instance.setup_db()

    # Save location
    db_instance.save_location(USERNAME, TEST_LOCATION)

    # Retrieve location
    retrieved = db_instance.get_location(USERNAME)
    assert retrieved == TEST_LOCATION


def test_get_location_returns_none_if_missing(db_instance):
    db_instance.setup_db()
    result = db_instance.get_location("nonexistent_user")
    assert result is None


def test_save_location_raises_database_error(monkeypatch):
    db = Database(":memory:")

    # Patch connect to raise DatabaseError
    monkeypatch.setattr("sqlite3.connect", lambda _: (_ for _ in ()).throw(sqlite3.DatabaseError("DB fail")))

    with pytest.raises(sqlite3.DatabaseError, match="DB fail"):
        db.save_location(USERNAME, TEST_LOCATION)


def test_get_location_raises_database_error(monkeypatch):
    db = Database(":memory:")

    # Patch connect to raise DatabaseError
    monkeypatch.setattr("sqlite3.connect", lambda _: (_ for _ in ()).throw(sqlite3.DatabaseError("DB fail")))

    with pytest.raises(sqlite3.DatabaseError, match="DB fail"):
        db.get_location(USERNAME)
