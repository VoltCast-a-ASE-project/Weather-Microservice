import pytest
from pydantic import ValidationError
from app.models.weather import (
    CurrentWeatherOverview,
    TodayWeatherOverview,
    WeatherOverview,
    HourWeatherData,
    DailyHourWeatherData,
    HourlyWeatherData,
    DayWeatherData,
    DailyWeatherData
)

# ----------------------------
# CurrentWeatherOverview
# ----------------------------
def test_current_weather_overview_success():
    data = CurrentWeatherOverview(description="Sunny", code=100, temperature=25.5)
    assert data.description == "Sunny"
    assert data.code == 100
    assert data.temperature == 25.5

def test_current_weather_overview_wrong_type():
    with pytest.raises(ValidationError):
        CurrentWeatherOverview(description=123, code="abc", temperature="hot")


# ----------------------------
# TodayWeatherOverview
# ----------------------------
def test_today_weather_overview_success():
    data = TodayWeatherOverview(
        description="Cloudy",
        code=200,
        temperature_min=15.0,
        temperature_max=22.0
    )
    assert data.temperature_min == 15.0
    assert data.temperature_max == 22.0

def test_today_weather_overview_wrong_type():
    with pytest.raises(ValidationError):
        TodayWeatherOverview(description=123, code="abc", temperature_min="low", temperature_max=None)


# ----------------------------
# WeatherOverview
# ----------------------------
def test_weather_overview_success():
    now = CurrentWeatherOverview(description="Sunny", code=100, temperature=25.5)
    today = TodayWeatherOverview(description="Cloudy", code=200, temperature_min=15, temperature_max=22)
    overview = WeatherOverview(now=now, today=today)
    assert overview.now.temperature == 25.5
    assert overview.today.temperature_max == 22

def test_weather_overview_wrong_type():
    with pytest.raises(ValidationError):
        WeatherOverview(now="bad", today=123)


# ----------------------------
# HourWeatherData
# ----------------------------
def test_hour_weather_data_success():
    hour = HourWeatherData(
        timestamp="2026-01-07T12:00:00Z",
        description="Rainy",
        code=300,
        temperature=18.5,
        rain=2.0,
        snowfall=0.0,
        cloud_cover=80.0,
        wind_speed=10.5
    )
    assert hour.rain == 2.0
    assert hour.wind_speed == 10.5

def test_hour_weather_data_wrong_type():
    with pytest.raises(ValidationError):
        HourWeatherData(timestamp=123, description=None, code="abc", temperature="hot",
                        rain="none", snowfall=[], cloud_cover="high", wind_speed=None)


# ----------------------------
# DailyHourWeatherData
# ----------------------------
def test_daily_hour_weather_data_success():
    hour = HourWeatherData(
        timestamp="2026-01-07T12:00:00Z",
        description="Sunny",
        code=100,
        temperature=20,
        rain=0,
        snowfall=0,
        cloud_cover=0,
        wind_speed=5
    )
    daily = DailyHourWeatherData(timestamp="2026-01-07", hours=[hour])
    assert len(daily.hours) == 1
    assert daily.hours[0].temperature == 20

def test_daily_hour_weather_data_wrong_type():
    with pytest.raises(ValidationError):
        DailyHourWeatherData(timestamp=123, hours="not a list")


# ----------------------------
# HourlyWeatherData
# ----------------------------
def test_hourly_weather_data_success():
    hour = HourWeatherData(
        timestamp="2026-01-07T12:00:00Z",
        description="Sunny",
        code=100,
        temperature=20,
        rain=0,
        snowfall=0,
        cloud_cover=0,
        wind_speed=5
    )
    daily = DailyHourWeatherData(timestamp="2026-01-07", hours=[hour])
    hourly = HourlyWeatherData(forecast=[daily])
    assert len(hourly.forecast) == 1
    assert hourly.forecast[0].hours[0].description == "Sunny"

def test_hourly_weather_data_wrong_type():
    with pytest.raises(ValidationError):
        HourlyWeatherData(forecast="not a list")


# ----------------------------
# DayWeatherData
# ----------------------------
def test_day_weather_data_success():
    day = DayWeatherData(
        timestamp="2026-01-07",
        description="Windy",
        code=400,
        temperature=22,
        rain=0,
        snowfall=0,
        wind_gust_max=15
    )
    assert day.wind_gust_max == 15

def test_day_weather_data_wrong_type():
    with pytest.raises(ValidationError):
        DayWeatherData(timestamp=None, description=123, code="bad", temperature="hot",
                       rain="none", snowfall="none", wind_gust_max="fast")


# ----------------------------
# DailyWeatherData
# ----------------------------
def test_daily_weather_data_success():
    day = DayWeatherData(
        timestamp="2026-01-07",
        description="Windy",
        code=400,
        temperature=22,
        rain=0,
        snowfall=0,
        wind_gust_max=15
    )
    daily = DailyWeatherData(days=[day])
    assert len(daily.days) == 1
    assert daily.days[0].description == "Windy"

def test_daily_weather_data_wrong_type():
    with pytest.raises(ValidationError):
        DailyWeatherData(days="not a list")
