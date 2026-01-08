from fastapi import FastAPI, Query
from httpx import Request
from starlette.responses import JSONResponse
from fastapi import Body
from app.core.errors import MappingError, ExternalApiError
from app.models.geocode import LocationRequest, SimpleLocation, UserLocation, User
from app.services.geocode import search_location
import sqlite3
from app.Database import Database
from app.services.weather import get_overview, get_hourly_data, get_daily_data

app = FastAPI(title="Weather & Location Microservice")
db = Database()

@app.on_event("startup")
def setup_db_at_startup():
    db.setup_db()  # creates tables once at startup

@app.get("/weather/hello")
async def root():
    return {"message": "Hello, Weather Microservice!"}

@app.post("/weather/overview")
async def get_overview_route(location: SimpleLocation = Body(...)):
    return await get_overview(location.lat, location.lon)

@app.post("/weather/forecast/hourly")
async def get_hourly_route(location: SimpleLocation = Body(...)):
    return await get_hourly_data(location.lat, location.lon)

@app.post("/weather/forecast/daily")
async def get_daily_route(location: SimpleLocation = Body(...)):
    return await get_daily_data(location.lat, location.lon)

@app.post("/weather/location/search")
async def search_location_route(data: LocationRequest = Body(...)):
    result = await search_location(data)
    #logger.info(f"Sending result to client: {result}")
    return result

@app.put("/weather/location")
async def set_location_route(data: UserLocation = Body(...)):
    db.save_location(data.username, data.location)
    return {"status": "success", "location": data.location.model_dump()}

@app.post("/weather/location")
async def get_location_route(data: User = Body(...)):
    location = db.get_location(data.username)
    if location is None:
        return {"status": "error", "message": "no location found"}
    return {"status": "success", "location": location.model_dump()}

# Error handling:
@app.exception_handler(MappingError)
async def mapping_error_handler_mapping(request: Request, exc: MappingError):
    return JSONResponse(
        status_code=500,
        content={"error": "MappingError", "message": str(exc)}
    )

@app.exception_handler(ExternalApiError)
async def mapping_error_handler_external(request: Request, exc: ExternalApiError):
    return JSONResponse(
        status_code=503,
        content={"error": "ExternalApiError", "message": str(exc)}
    )

@app.exception_handler(sqlite3.DatabaseError)
async def db_exception_handler(request: Request, exc: sqlite3.DatabaseError):
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred", "error": str(exc)}
    )
