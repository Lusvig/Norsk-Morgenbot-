"""Utility functions for Morgenbot."""

from morgenbot.utils.calculations import (
    calculate_daylight,
    calculate_wind_chill,
    format_large_number,
    get_clothing_advice,
)
from morgenbot.utils.date_utils import (
    days_until,
    format_countdown,
    format_norwegian_date,
    format_norwegian_date_with_week,
    get_greeting_time,
    is_weekday,
    is_weekend,
)
from morgenbot.utils.formatting import bold, code_block, italic, inline_code

__all__ = [
    # Calculations
    "calculate_wind_chill",
    "get_clothing_advice",
    "calculate_daylight",
    "format_large_number",
    # Date utils
    "format_norwegian_date",
    "format_norwegian_date_with_week",
    "days_until",
    "format_countdown",
    "get_greeting_time",
    "is_weekend",
    "is_weekday",
    # Formatting
    "bold",
    "italic",
    "code_block",
    "inline_code",
]
