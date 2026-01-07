import pytest
from app.models.weatherCodes import WEATHER_CODES, map_weather_code

# ----------------------------
# Test all valid codes
# ----------------------------
@pytest.mark.parametrize("code,expected", [(k, v) for k, v in WEATHER_CODES.items()])
def test_map_weather_code_valid(code, expected):
    result = map_weather_code(code)
    assert result == expected

# ----------------------------
# Test invalid codes
# ----------------------------
@pytest.mark.parametrize("invalid_code", [-1, 100, 999])
def test_map_weather_code_invalid(invalid_code):
    with pytest.raises(ValueError) as exc_info:
        map_weather_code(invalid_code)
    assert str(invalid_code) in str(exc_info.value)
