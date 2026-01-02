from fastapi import FastAPI, Query
from httpx import Request
from starlette.responses import JSONResponse
from fastapi import Body
from core.errors import MappingError, ExternalApiError
from models.geocode import LocationRequest
from services.geocode import get_location

app = FastAPI(title="Weather & Location Microservice")

@app.get("/")
async def root():
    return {"message": "Hello, Weather Microservice!"}

@app.post("/location")
async def location_route(data: LocationRequest = Body(...)):

    result = await get_location(data)
    #logger.info(f"Sending result to client: {result}")
    return result


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
