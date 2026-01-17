"""
Custom exceptions for Morgenbot.
"""

from __future__ import annotations


class MorgenbotError(Exception):
    """Base exception for alle Morgenbot-feil."""
    
    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)


class ConfigurationError(MorgenbotError):
    """Feil i konfigurasjon."""
    pass


class APIError(MorgenbotError):
    """Feil ved API-kall."""
    
    def __init__(
        self,
        message: str,
        service: str | None = None,
        status_code: int | None = None,
        *args: object,
    ) -> None:
        self.service = service
        self.status_code = status_code
        super().__init__(message, *args)


class WeatherAPIError(APIError):
    """Feil ved vær-API."""
    
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, service="met.no", *args)


class FinanceAPIError(APIError):
    """Feil ved finans-API."""
    pass


class DiscordError(MorgenbotError):
    """Feil ved Discord-kommunikasjon."""
    pass


class DataLoadError(MorgenbotError):
    """Feil ved lasting av data."""
    
    def __init__(self, message: str, filename: str | None = None, *args: object) -> None:
        self.filename = filename
        super().__init__(message, *args)


class ValidationError(MorgenbotError):
    """Valideringsfeil."""
    pass
