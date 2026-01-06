class AppError(Exception):
    """Base class for all application errors."""
    pass


class ExternalApiError(AppError):
    """Raised when an external API fails or returns unexpected data."""
    pass


class MappingError(AppError):
    """Raised when mapping from external or internal data fails."""
    pass
