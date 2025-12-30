from pydantic import BaseModel

class SimpleLocation(BaseModel):
    name: str
    lat: float
    lon: float

class Location(BaseModel):
    full_name: str
    lat: float
    lon: float
    house_number: str | None

class LocationList(BaseModel):
    locations: list[Location]
