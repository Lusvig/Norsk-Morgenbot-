"""
Tjenester for Morgenbot.
"""

from morgenbot.services.ai_service import AIService
from morgenbot.services.crypto_service import CryptoService
from morgenbot.services.discord_service import DiscordService
from morgenbot.services.electricity_service import ElectricityService
from morgenbot.services.finance_service import FinanceService
from morgenbot.services.news_service import NewsService
from morgenbot.services.sun_service import SunService
from morgenbot.services.weather_service import WeatherService

__all__ = [
    "AIService",
    "CryptoService",
    "DiscordService",
    "ElectricityService",
    "FinanceService",
    "NewsService",
    "SunService",
    "WeatherService",
]
