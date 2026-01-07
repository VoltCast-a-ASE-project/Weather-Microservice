from unittest.mock import AsyncMock, MagicMock
from app.services.weather import get_overview, get_hourly_data, get_daily_data, api_call_overview, api_call_hourly_forecast, api_call_daily_forecast
from app.models.weather import WeatherOverview, HourlyWeatherData, DailyWeatherData
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_get_overview_success():
    lat, lon = 12.34, 56.78

    # Mock response object
    mock_response = MagicMock()

    # Patch api_call_overview to return our mock response
    with patch("app.services.weather.api_call_overview", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = mock_response

        # Patch the mapper to just return a dummy WeatherOverview
        with patch("app.services.weather.map_openmeteo_overview") as mock_mapper:
            dummy_overview = WeatherOverview(
                now={"description": "Clear sky", "code": 0, "temperature": 25.0},
                today={"description": "Clear sky", "code": 0, "temperature_min": 20.0, "temperature_max": 26.0}
            )
            mock_mapper.return_value = dummy_overview

            result = await get_overview(lat, lon)

    assert isinstance(result, WeatherOverview)
    assert result.now.temperature == 25.0


@pytest.mark.asyncio
async def test_get_hourly_data_success():
    lat, lon = 12.34, 56.78

    mock_response = MagicMock()

    with patch("app.services.weather.api_call_hourly_forecast", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = mock_response

        with patch("app.services.weather.map_openmeteo_hourly_forecast") as mock_mapper:
            dummy_hourly = HourlyWeatherData(forecast=[])
            mock_mapper.return_value = dummy_hourly

            result = await get_hourly_data(lat, lon)

    assert isinstance(result, HourlyWeatherData)


@pytest.mark.asyncio
async def test_get_daily_data_success():
    lat, lon = 12.34, 56.78

    mock_response = MagicMock()

    with patch("app.services.weather.api_call_daily_forecast", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = mock_response

        with patch("app.services.weather.map_openmeteo_daily_forecast") as mock_mapper:
            dummy_daily = DailyWeatherData(days=[])
            mock_mapper.return_value = dummy_daily

            result = await get_daily_data(lat, lon)

    assert isinstance(result, DailyWeatherData)

@pytest.mark.asyncio
async def test_api_call_overview_direct():
    # Patch the client's weather_api method
    with patch("app.services.weather.overview_client.weather_api") as mock_api:
        mock_api.return_value = [{"foo": "bar"}]  # dummy API response
        result = await api_call_overview(12.34, 56.78)

    assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_api_call_hourly_forecast_direct():
    with patch("app.services.weather.hourly_forecast_client.weather_api") as mock_api:
        mock_api.return_value = [{"hour": 1}, {"hour": 2}]  # dummy hourly response
        result = await api_call_hourly_forecast(12.34, 56.78)

    # Only the first response is returned
    assert result == {"hour": 1}


@pytest.mark.asyncio
async def test_api_call_daily_forecast_direct():
    with patch("app.services.weather.daily_forecast_client.weather_api") as mock_api:
        mock_api.return_value = [{"day": "Monday"}, {"day": "Tuesday"}]  # dummy daily response
        result = await api_call_daily_forecast(12.34, 56.78)

    # Only the first response is returned
    assert result == {"day": "Monday"}