from app.services.utils import build_geocode_params
from app.services.config import GEOCODE_DEFAULT_PARAMS

def test_build_geocode_params_without_country():
    params = build_geocode_params(
        street="Main St",
        housenumber="42",
        city="Berlin",
        postalcode="10115"
    )

    assert params["street"] == "Main St 42"
    assert params["city"] == "Berlin"
    assert params["postalcode"] == "10115"

    # country should NOT be present
    assert "country" not in params

    # default params must be appended
    for key, value in GEOCODE_DEFAULT_PARAMS.items():
        assert params[key] == value


def test_build_geocode_params_with_country():
    params = build_geocode_params(
        street="Main St",
        housenumber="42",
        city="Berlin",
        postalcode="10115",
        country="DE"
    )

    assert params["street"] == "Main St 42"
    assert params["city"] == "Berlin"
    assert params["postalcode"] == "10115"
    assert params["country"] == "DE"

    # default params must still be present
    for key, value in GEOCODE_DEFAULT_PARAMS.items():
        assert params[key] == value