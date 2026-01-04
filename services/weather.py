import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

from mapper.weather import map_openmeteo_overview, map_openmeteo_hourly_forecast, map_openmeteo_daily_forecast
from models.weather import WeatherOverview, HourlyWeatherData, DailyWeatherData

BASE_URL = "https://api.open-meteo.com/v1/forecast"

overview_session = requests_cache.CachedSession('.cache_overview', expire_after=1800) # 30 min
overview_client = openmeteo_requests.Client(session=retry(overview_session, retries=5, backoff_factor=0.2))

hourly_forecast_session = requests_cache.CachedSession('.cache_hour_forecast', expire_after=3000) # 50 min
hourly_forecast_client = openmeteo_requests.Client(session=retry(hourly_forecast_session, retries=5, backoff_factor=0.2))

daily_forecast_session = requests_cache.CachedSession('.cache_daily_forecast', expire_after=1800) # 30 min
daily_forecast_client = openmeteo_requests.Client(session=retry(daily_forecast_session, retries=5, backoff_factor=0.2))

overview_params = {
	"current": ["weather_code", "temperature_2m"],
	"daily": ["weather_code", "temperature_2m_min", "temperature_2m_max"],
	"timezone": "auto",
	"forecast_days": 1,
}
hourly_params = {
	"hourly": ["weather_code", "temperature_2m", "rain", "snowfall", "cloud_cover", "wind_speed_10m"],
	"timezone": "auto",
}
daily_params = {
	"daily": ["weather_code", "temperature_2m_mean", "rain_sum", "snowfall_sum", "wind_gusts_10m_max"],
	"timezone": "auto",
}
async def api_call_overview(lat: float, lon: float):
	params = overview_params.copy()
	params["latitude"] = str(lat)
	params["longitude"] = str(lon)
	responses = overview_client.weather_api(BASE_URL, params=params)
	return responses[0]

async def api_call_hourly_forecast(lat: float, lon: float):
	params = hourly_params.copy()
	params["latitude"] = str(lat)
	params["longitude"] = str(lon)
	responses = hourly_forecast_client.weather_api(BASE_URL, params=params)
	return responses[0]

async def api_call_daily_forecast(lat: float, lon: float):
	params = daily_params.copy()
	params["latitude"] = str(lat)
	params["longitude"] = str(lon)
	responses = daily_forecast_client.weather_api(BASE_URL, params=params)
	return responses[0]

'''
params3 = {
	"latitude": 46.6024721,
	"longitude": 13.82663,
	"daily": ["weather_code", "temperature_2m_mean", "rain_sum", "snowfall_sum", "wind_gusts_10m_max"],
	"timezone": "auto",
}
responses3 = openmeteo.weather_api(url, params=params3)

# Process first location. Add a for-loop for multiple locations or weather models
response3 = responses3[0]
daily = response3.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_mean = daily.Variables(1).ValuesAsNumpy()
daily_rain_sum = daily.Variables(2).ValuesAsNumpy()
daily_snowfall_sum = daily.Variables(3).ValuesAsNumpy()
daily_wind_gusts_10m_max = daily.Variables(4).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["weather_code"] = daily_weather_code
daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
daily_data["rain_sum"] = daily_rain_sum
daily_data["snowfall_sum"] = daily_snowfall_sum
daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max

daily_dataframe = pd.DataFrame(data = daily_data)
print("\nDaily data\n", daily_dataframe)
'''
async def get_overview(lat: float, lon: float) -> WeatherOverview :
	response = await api_call_overview(lat, lon)
	return map_openmeteo_overview(response)

async def get_hourly_data(lat: float, lon: float) -> HourlyWeatherData :
	response = await api_call_hourly_forecast(lat, lon)
	return map_openmeteo_hourly_forecast(response)

async def get_daily_data(lat: float, lon: float) -> DailyWeatherData :
	response = await api_call_daily_forecast(lat, lon)
	return map_openmeteo_daily_forecast(response)
