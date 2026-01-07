import pytest
from app.core.errors import AppError, ExternalApiError, MappingError

def test_app_error():
    with pytest.raises(AppError):
        raise AppError("Test message")

def test_external_api_error():
    with pytest.raises(ExternalApiError):
        raise ExternalApiError("API failed")

def test_mapping_error():
    with pytest.raises(MappingError):
        raise MappingError("Mapping failed")
