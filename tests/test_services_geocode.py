import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.geocode import search_location
from app.models.geocode import LocationRequest, Location, SimpleLocation
import httpx
from app.core.errors import ExternalApiError

RAW_API_DATA = [
    {
        "display_name": "Main St 123, Townsville, Countryland",
        "lat": 12.34,
        "lon": 56.78,
        "address": {"house_number": "123"}
    }
]

@pytest.mark.asyncio
async def test_search_location_success():
    request = LocationRequest(
        street="Main St",
        houseNumber="123",
        city="Townsville",
        postalCode="12345",
        country="Countryland"
    )

    # Patch the mappers
    with patch("app.services.geocode.map_raw_to_location_list") as mock_raw_to_list, \
         patch("app.services.geocode.map_location_list_to_simple_location") as mock_to_simple:

        mock_raw_to_list.return_value = [
            Location(
                full_name="Main St 123, Townsville, Countryland",
                lat=12.34,
                lon=56.78,
                house_number="123"
            )
        ]
        mock_to_simple.return_value = [
            SimpleLocation(
                name="Main St 123, Townsville, Countryland",
                lat=12.34,
                lon=56.78
            )
        ]

        # Patch async client correctly
        async_mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = RAW_API_DATA
        async_mock_client.get = AsyncMock(return_value=mock_resp)
        async_mock_client.__aenter__.return_value = async_mock_client
        async_mock_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=async_mock_client):
            result = await search_location(request)

    assert len(result) == 1
    assert result[0].name == "Main St 123, Townsville, Countryland"



@pytest.mark.asyncio
async def test_search_location_no_results():
    request = LocationRequest(
        street="Empty St",
        houseNumber="0",
        city="Nowhere",
        postalCode="00000",
        country="Noland"
    )

    with patch("app.services.geocode.map_raw_to_location_list") as mock_raw_to_list, \
         patch("app.services.geocode.map_location_list_to_simple_location") as mock_to_simple:

        # Return a Location without house_number
        mock_raw_to_list.return_value = [
            Location(full_name="Empty St, Nowhere", lat=0, lon=0, house_number=None)
        ]
        mock_to_simple.return_value = []

        async_mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = [{"address": {}}]
        async_mock_client.get = AsyncMock(return_value=mock_resp)
        async_mock_client.__aenter__.return_value = async_mock_client
        async_mock_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=async_mock_client):
            result = await search_location(request)

    # No valid house_number, should return empty list
    assert result == []


@pytest.mark.asyncio
async def test_search_location_http_error():
    request = LocationRequest(
        street="Error St",
        houseNumber="1",
        city="Failtown",
        postalCode="11111",
        country="Errland"
    )

    # Mock response object (synchronous .raise_for_status and .json)
    mock_response = MagicMock()
    error_response = MagicMock()
    error_response.status_code = 500
    http_error = httpx.HTTPStatusError("Server error", request=None, response=error_response)
    mock_response.raise_for_status.side_effect = http_error
    mock_response.json.return_value = []  # irrelevant, raise_for_status triggers first

    # AsyncClient (async context manager)
    async_client_mock = AsyncMock()
    async_client_mock.__aenter__.return_value = async_client_mock
    async_client_mock.__aexit__.return_value = None
    async_client_mock.get.return_value = mock_response  # get() returns mock_response

    with patch("httpx.AsyncClient", return_value=async_client_mock):
        with pytest.raises(ExternalApiError) as exc_info:
            await search_location(request)

    assert "Geocoding API returned 500" in str(exc_info.value)


@pytest.mark.asyncio
async def test_search_location_request_error():
    request = LocationRequest(
        street="Down St",
        houseNumber="2",
        city="Timeout",
        postalCode="22222",
        country="Failland"
    )

    async_mock_client = AsyncMock()
    async_mock_client.get = AsyncMock(side_effect=httpx.RequestError("Connection failed", request=None))
    async_mock_client.__aenter__.return_value = async_mock_client
    async_mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=async_mock_client):
        with pytest.raises(ExternalApiError) as exc_info:
            await search_location(request)

    assert "Failed to reach geocoding API" in str(exc_info.value)


@pytest.mark.asyncio
async def test_search_location_invalid_json():
    request = LocationRequest(
        street="Bad JSON",
        houseNumber="3",
        city="Junktown",
        postalCode="33333",
        country="Badland"
    )

    # mock response with synchronous .json() raising ValueError
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = ValueError("Invalid JSON")

    async_client_mock = AsyncMock()
    async_client_mock.__aenter__.return_value = async_client_mock
    async_client_mock.__aexit__.return_value = None
    async_client_mock.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=async_client_mock):
        with pytest.raises(ExternalApiError) as exc_info:
            await search_location(request)

    assert "Geocoding API returned invalid JSON" in str(exc_info.value)