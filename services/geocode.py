import httpx

from core.errors import ExternalApiError
from mapper.geocode import map_raw_to_location_list, map_location_list_to_simple_location
from models.geocode import SimpleLocation, LocationRequest
from .config import GEOCODE_DEFAULT_PARAMS
from .utils import build_geocode_params
import logging

BASE_URL = "https://nominatim.openstreetmap.org/search"
#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)

async def search_location(input: LocationRequest) -> list[SimpleLocation]:
    params = build_geocode_params(input.street, input.houseNumber, input.city, input.postalCode, input.country)
    #full_url = httpx.URL(BASE_URL, params=params)
    #logger.info(f"Sending request to Nominatim: {full_url}")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(BASE_URL, params=params)
            resp.raise_for_status()
            raw_data = resp.json()
    except httpx.HTTPStatusError as e:
        raise ExternalApiError(
            f"Geocoding API returned {e.response.status_code}"
        ) from e
    except httpx.RequestError as e:
        raise ExternalApiError(
            "Failed to reach geocoding API"
        ) from e
    except ValueError as e: #raw_data = resp.json() failure
        raise ExternalApiError(
            "Geocoding API returned invalid JSON"
        ) from e

    data = map_raw_to_location_list(raw_data)
    # process
    # result must have a house_numer, to assure its some sort of building
    filtered = [
        location
        for location in data
        if location.house_number is not None
    ]
    if len(filtered) == 0:
        #raise ExternalApiError("No valid locations found (no house number)")
        return [] #return empty list, so the frontend can easily differ between error and no result
    # maybe save data if there is only one entry = result

    # map for minimal shipping
    response = map_location_list_to_simple_location(filtered)
    return (response)