from app.core.errors import MappingError
from app.models.geocode import SimpleLocation, Location


def map_raw_to_location_list(raw_data: list[dict]) -> list[Location]:
    """Maps Nominatim API response to our simplified model."""
    if not isinstance(raw_data, list):
        raise MappingError("Invalid raw_data format: raw_data is not a list.")
    mapped: list[Location] = []
    try:
        for item in raw_data:
            mapped.append(Location(
                full_name=item.get("display_name"),
                lat=float(item.get("lat")),
                lon=float(item.get("lon")),
                house_number=item.get("address", {}).get("house_number") or None
            ))
    except Exception as e:
        raise MappingError(f"Invalid raw_data format: {e}")
    return mapped


def map_location_list_to_simple_location(location_list: list[Location]) -> list[SimpleLocation]:
    if not isinstance(location_list, list):
        raise MappingError("Invalid input format: location_list is not a list.")
    mapped: list[SimpleLocation] = []

    for item in location_list:
        mapped.append(SimpleLocation(
            name=item.full_name,
            lat=item.lat,
            lon=item.lon
        ))
    return mapped
