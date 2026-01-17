"""
Hovedapplikasjon for Morgenbot.

Orkestrerer alle tjenester og bygger den endelige Discord-meldingen.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from typing import TYPE_CHECKING

import structlog

from morgenbot.builders.message_builder import MessageBuilder
from morgenbot.config.settings import Settings
from morgenbot.exceptions.errors import MorgenbotError
from morgenbot.services import (
    AIService,
    CryptoService,
    DiscordService,
    ElectricityService,
    FinanceService,
    NewsService,
    SunService,
    WeatherService,
)

if TYPE_CHECKING:
    from morgenbot.models.discord import DiscordMessage


logger = structlog.get_logger(__name__)


class Morgenbot:
    """
    Hovedklasse for Morgenbot-applikasjonen.
    
    Koordinerer alle tjenester og bygger den endelige meldingen.
    
    Attributes:
        settings: Applikasjonskonfigurasjon
        weather_service: Tjeneste for værdata
        sun_service: Tjeneste for sol-data
        news_service: Tjeneste for nyheter
        finance_service: Tjeneste for aksjer og valuta
        crypto_service: Tjeneste for kryptovaluta
        electricity_service: Tjeneste for strømpriser
        ai_service: Tjeneste for AI-generert innhold
        discord_service: Tjeneste for Discord-kommunikasjon
        message_builder: Bygger Discord-meldinger
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialiserer Morgenbot med gitte innstillinger.
        
        Args:
            settings: Applikasjonskonfigurasjon
        """
        self.settings = settings
        self._init_services()
        self.message_builder = MessageBuilder(settings)
        
        logger.info(
            "morgenbot_initialized",
            city=settings.city,
            ai_enabled=settings.groq_api_key is not None,
        )

    def _init_services(self) -> None:
        """Initialiserer alle tjenester."""
        self.weather_service = WeatherService(self.settings)
        self.sun_service = SunService(self.settings)
        self.news_service = NewsService(self.settings)
        self.finance_service = FinanceService(self.settings)
        self.crypto_service = CryptoService(self.settings)
        self.electricity_service = ElectricityService(self.settings)
        self.ai_service = AIService(self.settings) if self.settings.groq_api_key else None
        self.discord_service = DiscordService(self.settings)

    async def gather_data(self) -> dict:
        """
        Samler inn all data fra tjenester asynkront.
        
        Returns:
            Dict med all innsamlet data
        """
        logger.info("gathering_data_started")
        
        # Kjør alle API-kall parallelt
        results = await asyncio.gather(
            self.weather_service.get_weather(self.settings.city),
            self.sun_service.get_sun_times(self.settings.city),
            self.news_service.get_news(),
            self.finance_service.get_stocks_and_currency(),
            self.crypto_service.get_prices(),
            self.electricity_service.get_prices(self.settings.city),
            return_exceptions=True,
        )
        
        # Prosesser resultater og logg eventuelle feil
        keys = ["weather", "sun", "news", "finance", "crypto", "electricity"]
        data = {}
        
        for key, result in zip(keys, results, strict=True):
            if isinstance(result, Exception):
                logger.warning(f"service_failed", service=key, error=str(result))
                data[key] = None
            else:
                data[key] = result
        
        # AI-hilsning (avhenger av annen data)
        if self.ai_service and data.get("weather"):
            try:
                data["ai_greeting"] = await self.ai_service.generate_greeting(data)
            except Exception as e:
                logger.warning("ai_greeting_failed", error=str(e))
                data["ai_greeting"] = None
        else:
            data["ai_greeting"] = None
        
        logger.info("gathering_data_completed")
        return data

    async def build_message(self) -> DiscordMessage:
        """
        Bygger komplett Discord-melding.
        
        Returns:
            Ferdig formatert Discord-melding
        """
        data = await self.gather_data()
        return self.message_builder.build(data)

    async def send_message(self) -> bool:
        """
        Sender morgenmeldingen til Discord.
        
        Returns:
            True hvis meldingen ble sendt, False ellers
        """
        try:
            message = await self.build_message()
            success = await self.discord_service.send(message)
            
            if success:
                logger.info("message_sent_successfully")
            else:
                logger.error("message_send_failed")
            
            return success
            
        except MorgenbotError as e:
            logger.error("morgenbot_error", error=str(e))
            return False

    async def run(self) -> int:
        """
        Kjører Morgenbot.
        
        Returns:
            Exit-kode (0 for suksess, 1 for feil)
        """
        logger.info(
            "morgenbot_started",
            version=self.settings.version,
            city=self.settings.city,
            timestamp=datetime.now().isoformat(),
        )
        
        success = await self.send_message()
        
        logger.info(
            "morgenbot_completed",
            success=success,
            timestamp=datetime.now().isoformat(),
        )
        
        return 0 if success else 1


def configure_logging(debug: bool = False) -> None:
    """
    Konfigurerer strukturert logging.
    
    Args:
        debug: Om debug-logging skal aktiveres
    """
    import structlog
    import structlog.processors
    
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]
    
    if debug:
        processors.append(structlog.dev.set_exc_info)
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()
    
    processors.append(structlog.processors.TimeStamper(fmt="iso"))
    processors.append(renderer)
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            structlog.logging.DEBUG if debug else structlog.logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def main() -> None:
    """Hovedfunksjon - entry point for applikasjonen."""
    try:
        settings = Settings()
        configure_logging(debug=settings.debug)
        
        bot = Morgenbot(settings)
        exit_code = asyncio.run(bot.run())
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("morgenbot_interrupted")
        sys.exit(130)
    except Exception as e:
        logger.exception("morgenbot_crashed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
