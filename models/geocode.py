from pydantic import BaseModel
from typing import Optional

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

class LocationRequest(BaseModel):
    street: str
    houseNumber: str
    city: str
    postalCode: str
    country: Optional[str] = None