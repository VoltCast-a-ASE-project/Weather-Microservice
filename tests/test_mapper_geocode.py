import pytest
from app.mapper.geocode import map_raw_to_location_list, map_location_list_to_simple_location
from app.models.geocode import Location, SimpleLocation
from app.core.errors import MappingError

RAW_VALID = [
    {
        "display_name": "123 Main St, Townsville, Countryland",
        "lat": "10.5",
        "lon": "20.5",
        "address": {"house_number": "123"}
    },
    {
        "display_name": "456 Side St, Villagetown, Countryland",
        "lat": "11.0",
        "lon": "21.0",
        "address": {}  # no house number
    }
]

RAW_INVALID_LAT = [
    {
        "display_name": "Bad Lat",
        "lat": "not-a-float",
        "lon": "20.5",
        "address": {"house_number": "1"}
    }
]

def test_map_raw_to_location_list_success():
    result = map_raw_to_location_list(RAW_VALID)
    assert isinstance(result, list)
    assert all(isinstance(item, Location) for item in result)
    assert result[0].house_number == "123"
    assert result[1].house_number is None
    assert result[0].lat == 10.5  # converted to float

def test_map_raw_to_location_list_invalid_type():
    with pytest.raises(MappingError):
        map_raw_to_location_list("not a list")

def test_map_raw_to_location_list_invalid_values():
    with pytest.raises(MappingError):
        map_raw_to_location_list(RAW_INVALID_LAT)
def test_map_location_list_to_simple_location_success():
    locations = map_raw_to_location_list(RAW_VALID)
    result = map_location_list_to_simple_location(locations)
    assert isinstance(result, list)
    assert all(isinstance(item, SimpleLocation) for item in result)
    assert result[0].name == locations[0].full_name
    assert result[0].lat == locations[0].lat
    assert result[0].lon == locations[0].lon

def test_map_location_list_to_simple_location_invalid_type():
    with pytest.raises(MappingError):
        map_location_list_to_simple_location("not a list")
