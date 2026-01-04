import pandas as pd
import pytz

from models.weather import *
from models.weatherCodes import map_weather_code

def map_openmeteo_overview(response) -> WeatherOverview:
    current = response.Current()
    daily = response.Daily()

    currentCode = int(current.Variables(0).Value())
    todayCode = int(daily.Variables(0).ValuesAsNumpy()[0])

    return WeatherOverview(
        now=CurrentWeatherOverview(
            description=map_weather_code(currentCode),
            code=currentCode,
            temperature=float(current.Variables(1).Value())
        ),
        today=TodayWeatherOverview(
            description=map_weather_code(todayCode),
            code=todayCode,
            temperature_min=float(daily.Variables(1).ValuesAsNumpy()[0]),
            temperature_max=float(daily.Variables(2).ValuesAsNumpy()[0])
        )
    )

def map_openmeteo_hourly_forecast(response) -> HourlyWeatherData:
    utc_offset_seconds = response.UtcOffsetSeconds()
    local_tz = pytz.FixedOffset(utc_offset_seconds / 60)  # pytz expects minutes

    hourly = response.Hourly()
    hourly_weather_code = hourly.Variables(0).ValuesAsNumpy()
    hourly_temperature_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_rain = hourly.Variables(2).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(3).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()

    hourly_data = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert(local_tz),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_convert(local_tz),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )
    daily: list[DailyHourWeatherData] = []
    current_day = None
    current_day_hours: list[HourWeatherData] = []

    for i, timestamp in enumerate(hourly_data):
        day_str = timestamp.date().isoformat()
        hourEntry = HourWeatherData(
            timestamp=str(timestamp),
            description=map_weather_code(int(hourly_weather_code[i])),
            code=int(hourly_weather_code[i]),
            temperature=float(hourly_temperature_2m[i]),
            rain=float(hourly_rain[i]),
            snowfall=float(hourly_snowfall[i]), # Maybe unit conversion
            cloud_cover=int(hourly_cloud_cover[i]),
            wind_speed=float(hourly_wind_speed_10m[i]),
        )
        if current_day is None:
            current_day = day_str
            current_day_hours.append(hourEntry)
        elif day_str == current_day:
            current_day_hours.append(hourEntry)
        else:
            daily.append(
                DailyHourWeatherData(
                    timestamp=str(current_day),
                    hours=current_day_hours
                )
            )
            current_day = day_str
            current_day_hours = [hourEntry]

    if current_day_hours:
        daily.append(
            DailyHourWeatherData(
                timestamp=str(current_day),
                hours=current_day_hours
            )
        )
    return HourlyWeatherData(
        forecast=daily
    )

def map_openmeteo_daily_forecast(response) -> DailyWeatherData:
    utc_offset_seconds = response.UtcOffsetSeconds()
    local_tz = pytz.FixedOffset(utc_offset_seconds / 60)  # pytz expects minutes

    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_mean = daily.Variables(1).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(2).ValuesAsNumpy()
    daily_snowfall_sum = daily.Variables(3).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(4).ValuesAsNumpy()

    daily_data = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True).tz_convert(local_tz),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True).tz_convert(local_tz),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )

    daily: list[DayWeatherData] = []

    for i, timestamp in enumerate(daily_data):
        dayEntry = DayWeatherData(
            timestamp=str(timestamp),
            description=map_weather_code(int(daily_weather_code[i])),
            code=int(daily_weather_code[i]),
            temperature=float(daily_temperature_2m_mean[i]),
            rain=float(daily_rain_sum[i]),
            snowfall=float(daily_snowfall_sum[i]), # Maybe unit conversion
            wind_gust_max=float(daily_wind_gusts_10m_max[i]),
        )
        daily.append(dayEntry)

    return DailyWeatherData(daily=daily)


