"""Data models for Morgenbot."""

from morgenbot.models.calendar import (
    CalendarData,
    Event,
    HistoricalEvent,
    Holiday,
    NameDay,
    Vacation,
)
from morgenbot.models.discord import (
    DiscordMessage,
    Embed,
    EmbedAuthor,
    EmbedField,
    EmbedFooter,
    EmbedImage,
    EmbedThumbnail,
)
from morgenbot.models.finance import (
    CryptoPrice,
    CurrencyRate,
    ElectricityPrice,
    FinanceData,
    StockQuote,
    TrendDirection,
)
from morgenbot.models.news import NewsData, NewsItem
from morgenbot.models.weather import (
    CurrentWeather,
    SunTimes,
    WeatherCondition,
    WeatherData,
)

__all__ = [
    # Weather models
    "WeatherCondition",
    "CurrentWeather",
    "SunTimes",
    "WeatherData",
    # Finance models
    "TrendDirection",
    "StockQuote",
    "CurrencyRate",
    "CryptoPrice",
    "ElectricityPrice",
    "FinanceData",
    # Calendar models
    "Holiday",
    "Vacation",
    "Event",
    "HistoricalEvent",
    "NameDay",
    "CalendarData",
    # News models
    "NewsItem",
    "NewsData",
    # Discord models
    "EmbedField",
    "EmbedFooter",
    "EmbedAuthor",
    "EmbedThumbnail",
    "EmbedImage",
    "Embed",
    "DiscordMessage",
]
