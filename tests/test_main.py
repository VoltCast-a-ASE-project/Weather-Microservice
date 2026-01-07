import pytest
import sqlite3
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app, db
from app.models.geocode import SimpleLocation
from fastapi.testclient import TestClient

# Use FastAPI test client for sync tests
client = TestClient(app)

# Sample payloads
SIMPLE_LOCATION = {"lat": 12.34, "lon": 56.78, "name": "Test Place"}
LOCATION_REQUEST = {
    "street": "Main St",
    "houseNumber": "123",
    "city": "Townsville",
    "postalCode": "12345",
    "country": "Countryland"
}
USER_LOCATION = {"username": "alice", "location": SIMPLE_LOCATION}
USER = {"username": "alice"}

@pytest.mark.asyncio
async def test_weather_routes(monkeypatch):
    # Mock weather service functions
    async_mock_overview = AsyncMock(return_value={"now": {}, "today": {}})
    async_mock_hourly = AsyncMock(return_value={"forecast": []})
    async_mock_daily = AsyncMock(return_value={"days": []})

    monkeypatch.setattr("app.main.get_overview", async_mock_overview)
    monkeypatch.setattr("app.main.get_hourly_data", async_mock_hourly)
    monkeypatch.setattr("app.main.get_daily_data", async_mock_daily)

    # Test overview route
    resp = client.post("/weather/overview", json=SIMPLE_LOCATION)
    assert resp.status_code == 200
    assert resp.json() == {"now": {}, "today": {}}
    async_mock_overview.assert_awaited_once_with(12.34, 56.78)

    # Test hourly forecast route
    resp = client.post("/weather/forecast/hourly", json=SIMPLE_LOCATION)
    assert resp.status_code == 200
    assert resp.json() == {"forecast": []}
    async_mock_hourly.assert_awaited_once_with(12.34, 56.78)

    # Test daily forecast route
    resp = client.post("/weather/forecast/daily", json=SIMPLE_LOCATION)
    assert resp.status_code == 200
    assert resp.json() == {"days": []}
    async_mock_daily.assert_awaited_once_with(12.34, 56.78)

@pytest.mark.asyncio
async def test_location_search_route(monkeypatch):
    # Mock search_location service
    async_mock_search = AsyncMock(return_value=[{"name": "Test Place"}])
    monkeypatch.setattr("app.main.search_location", async_mock_search)

    resp = client.post("/location/search", json=LOCATION_REQUEST)
    assert resp.status_code == 200
    assert resp.json() == [{"name": "Test Place"}]
    async_mock_search.assert_awaited_once()

@pytest.mark.asyncio
async def test_set_and_get_location_routes(monkeypatch):
    # Mock db methods
    mock_save = MagicMock()
    mock_get = MagicMock(return_value=SimpleLocation(**SIMPLE_LOCATION))
    monkeypatch.setattr("app.main.db.save_location", mock_save)
    monkeypatch.setattr("app.main.db.get_location", mock_get)

    # Test set_location
    resp = client.put("/location", json=USER_LOCATION)
    assert resp.status_code == 200
    assert resp.json() == {"status": "success", "location": SIMPLE_LOCATION}

    # Check that save_location was called correctly
    mock_save.assert_called_once()
    saved_username, saved_location = mock_save.call_args[0]
    assert saved_username == "alice"
    assert isinstance(saved_location, SimpleLocation)
    assert saved_location.model_dump() == SIMPLE_LOCATION

    # Test get_location
    resp = client.post("/location", json=USER)
    assert resp.status_code == 200
    assert resp.json() == {"status": "success", "location": SIMPLE_LOCATION}

    mock_get.assert_called_once_with("alice")

@pytest.mark.asyncio
async def test_get_location_no_result(monkeypatch):
    # Mock db.get_location to return None
    monkeypatch.setattr("app.main.db.get_location", MagicMock(return_value=None))

    resp = client.post("/location", json=USER)
    assert resp.status_code == 200
    assert resp.json() == {"status": "error", "message": "no location found"}

@pytest.mark.asyncio
async def test_exception_handlers(monkeypatch):
    from app.core.errors import MappingError, ExternalApiError

    # Test MappingError handler
    resp = client.get("/weather")  # normal route
    assert resp.status_code == 200

    # Manually trigger MappingError via endpoint
    async def raise_mapping(*args, **kwargs):
        raise MappingError("bad mapping")

    monkeypatch.setattr("app.main.get_overview", raise_mapping)
    resp = client.post("/weather/overview", json=SIMPLE_LOCATION)
    assert resp.status_code == 500
    assert resp.json() == {"error": "MappingError", "message": "bad mapping"}

    # Manually trigger ExternalApiError
    async def raise_external(*args, **kwargs):
        raise ExternalApiError("external fail")

    monkeypatch.setattr("app.main.get_overview", raise_external)
    resp = client.post("/weather/overview", json=SIMPLE_LOCATION)
    assert resp.status_code == 503
    assert resp.json() == {"error": "ExternalApiError", "message": "external fail"}

def test_startup_event_calls_setup_db(monkeypatch):
    called = {}

    # Patch db.setup_db to track if it was called
    def mock_setup_db():
        called["yes"] = True

    monkeypatch.setattr(db, "setup_db", mock_setup_db)

    # Manually trigger startup events
    for fn in app.router.on_startup:
        fn()

    assert called.get("yes") is True


# ---------- NEW TEST: sqlite3.DatabaseError handler ----------
def test_db_exception_handler():
    # Add a temporary route that raises DatabaseError
    @app.get("/raise-db-error")
    def raise_db_error():
        raise sqlite3.DatabaseError("boom!")

    response = client.get("/raise-db-error")
    assert response.status_code == 500
    assert response.json() == {
        "detail": "A database error occurred",
        "error": "boom!"
    }