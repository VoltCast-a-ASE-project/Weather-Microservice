from .config import GEOCODE_DEFAULT_PARAMS

def build_geocode_params(street, housenumber, city, postalcode, country=None):
    params = {
        "street": f"{street} {housenumber}",
        "city": city,
        "postalcode": postalcode
    }
    if country:
        params["country"] = country

    # Append defaults at the end
    params.update(GEOCODE_DEFAULT_PARAMS)
    return params
