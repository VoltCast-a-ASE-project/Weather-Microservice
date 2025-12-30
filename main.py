from fastapi import FastAPI, Query
from httpx import Request
from starlette.responses import JSONResponse

from core.errors import MappingError, ExternalApiError
from services.geocode import get_location

app = FastAPI(title="Weather & Location Microservice")

@app.get("/")
async def root():
    return {"message": "Hello, Weather Microservice!"}

@app.get("/location")
async def location_route(
        street: str = Query(..., description="Street address"),
        housenumber: str = Query(..., description="House number"),
        city: str = Query(..., description="City name"),
        postalcode: str = Query(..., description="Postal code"),
        country: str | None = Query(None, description="Country name")
):
    """
    Example: /location?street=mystreet&housenumber=myhousenumber&city=mycity
    """
    return await get_location(street, housenumber, city, postalcode, country)

@app.exception_handler(MappingError)
async def mapping_error_handler(request: Request, exc: MappingError):
    return JSONResponse(
        status_code=500,
        content={"error": "MappingError", "message": str(exc)}
    )

@app.exception_handler(ExternalApiError)
async def mapping_error_handler(request: Request, exc: ExternalApiError):
    return JSONResponse(
        status_code=503,
        content={"error": "ExternalApiError", "message": str(exc)}
    )
