import pytest
from pydantic import ValidationError
from app.models.geocode import (
    SimpleLocation,
    Location,
    LocationList,
    LocationRequest,
    UserLocation,
    User
)

# -----------------------------
# Tests for SimpleLocation
# -----------------------------
def test_simple_location_valid():
    loc = SimpleLocation(name="Main St 123", lat=12.34, lon=56.78)
    assert loc.name == "Main St 123"
    assert loc.lat == 12.34
    assert loc.lon == 56.78

def test_simple_location_missing_field():
    with pytest.raises(ValidationError) as e:
        SimpleLocation(lat=12.34, lon=56.78)  # missing 'name'
    assert "name" in str(e.value)

def test_simple_location_wrong_type():
    with pytest.raises(ValidationError):
        SimpleLocation(name="Test", lat="not a float", lon=56.78)

# -----------------------------
# Tests for Location
# -----------------------------
def test_location_valid():
    loc = Location(full_name="Main St 123, Townsville", lat=12.34, lon=56.78, house_number="123")
    assert loc.house_number == "123"
    assert loc.lat == 12.34

def test_location_optional_house_number():
    loc = Location(full_name="Somewhere", lat=0.0, lon=0.0, house_number=None)
    assert loc.house_number is None

def test_location_missing_required_field():
    with pytest.raises(ValidationError):
        Location(lat=0.0, lon=0.0, house_number="1")  # missing full_name

# -----------------------------
# Tests for LocationList
# -----------------------------
def test_location_list_valid():
    loc1 = Location(full_name="A", lat=1.0, lon=2.0, house_number="1")
    loc2 = Location(full_name="B", lat=3.0, lon=4.0, house_number="2")
    loc_list = LocationList(locations=[loc1, loc2])
    assert len(loc_list.locations) == 2
    assert loc_list.locations[0].full_name == "A"

def test_location_list_wrong_type():
    with pytest.raises(ValidationError):
        LocationList(locations="not a list")  # should be list of Location

# -----------------------------
# Tests for LocationRequest
# -----------------------------
def test_location_request_valid():
    req = LocationRequest(
        street="Main St",
        houseNumber="123",
        city="Townsville",
        postalCode="12345",
        country="Countryland"
    )
    assert req.street == "Main St"
    assert req.country == "Countryland"

def test_location_request_optional_country():
    req = LocationRequest(
        street="Main St",
        houseNumber="123",
        city="Townsville",
        postalCode="12345"
    )
    assert req.country is None

def test_location_request_missing_required():
    with pytest.raises(ValidationError):
        LocationRequest(street="A", houseNumber="1", city="B", postalCode=None)

# -----------------------------
# Tests for UserLocation
# -----------------------------
def test_user_location_valid():
    simple_loc = SimpleLocation(name="Home", lat=12.0, lon=34.0)
    user_loc = UserLocation(username="alice", location=simple_loc)
    assert user_loc.username == "alice"
    assert user_loc.location.lat == 12.0

def test_user_location_wrong_type():
    with pytest.raises(ValidationError):
        UserLocation(username="bob", location=[1, 2, 3])

# -----------------------------
# Tests for User
# -----------------------------
def test_user_valid():
    user = User(username="alice")
    assert user.username == "alice"

def test_user_missing_field():
    with pytest.raises(ValidationError):
        User()  # missing username
