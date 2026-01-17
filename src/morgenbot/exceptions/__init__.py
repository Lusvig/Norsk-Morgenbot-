"""Custom exceptions for Morgenbot."""

from morgenbot.exceptions.errors import (
    APIError,
    ConfigurationError,
    DataLoadError,
    DiscordError,
    FinanceAPIError,
    MorgenbotError,
    ValidationError,
    WeatherAPIError,
)

__all__ = [
    "MorgenbotError",
    "ConfigurationError",
    "APIError",
    "WeatherAPIError",
    "FinanceAPIError",
    "DiscordError",
    "DataLoadError",
    "ValidationError",
]
