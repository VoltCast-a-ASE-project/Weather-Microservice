from pydantic import BaseModel

class CurrentWeatherOverview(BaseModel):
    description: str
    code: int
    temperature: float

class TodayWeatherOverview(BaseModel):
    description: str
    code: int
    temperature_min: float
    temperature_max: float

class WeatherOverview(BaseModel):
    now: CurrentWeatherOverview
    today: TodayWeatherOverview

class HourWeatherData(BaseModel):
    timestamp: str
    description: str
    code: int
    temperature: float
    rain: float
    snowfall: float
    cloud_cover: float
    wind_speed: float

class DailyHourWeatherData(BaseModel):
    timestamp: str
    hours: list[HourWeatherData]

class HourlyWeatherData(BaseModel):
    forecast: list[DailyHourWeatherData]

class DayWeatherData(BaseModel):
    timestamp: str
    description: str
    code: int
    temperature: float
    rain: float
    snowfall: float
    wind_gust_max: float

class DailyWeatherData(BaseModel):
    days: list[DayWeatherData]
