from app.mapper.weather import map_openmeteo_overview
from app.models.weather import WeatherOverview
from unittest.mock import MagicMock
from app.mapper.weather import map_openmeteo_hourly_forecast
from app.models.weather import HourlyWeatherData
from app.mapper.weather import map_openmeteo_daily_forecast
from app.models.weather import DailyWeatherData

def test_map_openmeteo_overview_success():
    # Mock the response
    response = MagicMock()

    # Current
    current = MagicMock()
    current.Variables.return_value.Value.side_effect = [1, 23.5]  # code, temp
    response.Current.return_value = current

    # Daily
    daily = MagicMock()
    daily.Variables.return_value.ValuesAsNumpy.return_value = [2, 10.0, 20.0]  # code, temp_min, temp_max
    response.Daily.return_value = daily

    # Override Variables(index) behavior
    def current_variables(index):
        v = MagicMock()
        v.Value.return_value = [1, 23.5][index]
        return v

    current.Variables.side_effect = current_variables

    def daily_variables(index):
        v = MagicMock()
        v.ValuesAsNumpy.return_value = [[2, ], [10.0, ], [20.0, ]][index]
        return v

    daily.Variables.side_effect = daily_variables

    result = map_openmeteo_overview(response)
    assert isinstance(result, WeatherOverview)
    assert result.now.code == 1
    assert result.now.temperature == 23.5
    assert result.today.code == 2
    assert result.today.temperature_min == 10.0
    assert result.today.temperature_max == 20.0

def test_map_openmeteo_hourly_forecast_full_coverage():
    # Mock response
    response = MagicMock()

    # Mock Hourly data
    hourly = MagicMock()
    # 2-day period: Jan 1 and Jan 2, 2021, hourly
    hourly.Time.return_value = 1609459200   # Jan 1 00:00 UTC
    hourly.TimeEnd.return_value = 1609632000 # Jan 3 00:00 UTC (48 hours)
    hourly.Interval.return_value = 3600  # 1 hour

    # Variables: weather_code, temperature, rain, snowfall, cloud, wind
    data_arrays = [
        [0]*48,           # weather codes
        [10.0 + i for i in range(48)],  # temperature
        [0.0]*48,         # rain
        [0.0]*48,         # snowfall
        [10 + i for i in range(48)],    # cloud cover
        [1.0 + i*0.1 for i in range(48)] # wind speed
    ]

    # Each call to Variables(index) returns a MagicMock with ValuesAsNumpy
    def var_side_effect(index):
        v = MagicMock()
        v.ValuesAsNumpy.return_value = data_arrays[index]
        return v

    hourly.Variables.side_effect = var_side_effect

    response.Hourly.return_value = hourly
    response.UtcOffsetSeconds.return_value = 120  # +2 minutes offset

    # Call mapper
    result = map_openmeteo_hourly_forecast(response)

    # Assertions
    assert isinstance(result, HourlyWeatherData)
    # There should be 2 days in forecast
    assert len(result.forecast) == 2
    # Each day has 24 hours
    for day in result.forecast:
        assert len(day.hours) == 24
    # Check first hour values
    first_hour = result.forecast[0].hours[0]
    assert first_hour.temperature == 10.0
    assert first_hour.code == 0
    assert first_hour.description == "Clear sky"


def test_map_openmeteo_daily_forecast_success():
    response = MagicMock()

    daily = MagicMock()
    daily.Time.return_value = 1609459200
    daily.TimeEnd.return_value = 1609632000  # 2 days later
    daily.Interval.return_value = 86400  # 1 day

    data_arrays = [
        [0, 1],  # codes
        [15.0, 16.0],  # temp_mean
        [0.0, 0.1],  # rain
        [0.0, 0.0],  # snowfall
        [5.0, 6.0]  # wind gusts
    ]

    def var_side_effect(index):
        v = MagicMock()
        v.ValuesAsNumpy.return_value = data_arrays[index]
        return v

    daily.Variables.side_effect = var_side_effect
    response.Daily.return_value = daily
    response.UtcOffsetSeconds.return_value = 0

    result = map_openmeteo_daily_forecast(response)
    assert isinstance(result, DailyWeatherData)
    assert len(result.days) == 2
    assert result.days[0].temperature == 15.0