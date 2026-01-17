"""Field builders for Discord embeds."""

from morgenbot.builders.field_builders.calendar_field import build_calendar_fields
from morgenbot.builders.field_builders.entertainment_field import (
    build_entertainment_field,
)
from morgenbot.builders.field_builders.finance_field import build_finance_fields
from morgenbot.builders.field_builders.news_field import build_news_fields
from morgenbot.builders.field_builders.weather_field import build_weather_field

__all__ = [
    "build_calendar_fields",
    "build_entertainment_field",
    "build_finance_fields",
    "build_news_fields",
    "build_weather_field",
]
