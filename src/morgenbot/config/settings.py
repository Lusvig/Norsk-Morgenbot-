"""
Konfigurasjon og innstillinger for Morgenbot.

Bruker Pydantic Settings for validering og lasting fra miljøvariabler.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, HttpUrl, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Applikasjonsinnstillinger.
    
    Lastes automatisk fra miljøvariabler og .env-fil.
    
    Attributes:
        discord_webhook: Discord webhook URL for sending av meldinger
        groq_api_key: API-nøkkel for Groq AI (valgfri)
        city: Standard by for vær og strømpriser
        debug: Om debug-modus er aktivert
        request_timeout: Timeout for HTTP-forespørsler i sekunder
        cache_ttl: Time-to-live for cache i sekunder
        user_agent: User-Agent header for API-kall
        version: Applikasjonsversjon
        data_dir: Mappe for datafiler
        log_level: Logging-nivå
        retry_attempts: Antall forsøk ved feil
        retry_delay: Forsinkelse mellom forsøk i sekunder
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Påkrevde innstillinger
    discord_webhook: HttpUrl = Field(
        ...,
        description="Discord webhook URL",
        examples=["https://discord.com/api/webhooks/..."],
    )

    # Valgfrie innstillinger
    groq_api_key: SecretStr | None = Field(
        default=None,
        description="Groq API-nøkkel for AI-funksjoner",
    )
    
    city: str = Field(
        default="Moss",
        description="Standard by for vær og strømpriser",
        min_length=2,
        max_length=50,
    )
    
    debug: bool = Field(
        default=False,
        description="Aktiver debug-modus",
    )
    
    request_timeout: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Timeout for HTTP-forespørsler i sekunder",
    )
    
    cache_ttl: int = Field(
        default=300,
        ge=0,
        le=3600,
        description="Cache TTL i sekunder",
    )
    
    user_agent: str = Field(
        default="Morgenbot/3.0 (https://github.com/username/morgenbot)",
        description="User-Agent for API-kall",
    )
    
    version: str = Field(
        default="3.0.0",
        description="Applikasjonsversjon",
    )
    
    data_dir: Path = Field(
        default=Path(__file__).parent.parent.parent.parent / "data",
        description="Mappe for datafiler",
    )
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging-nivå",
    )
    
    retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Antall retry-forsøk",
    )
    
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=30.0,
        description="Forsinkelse mellom retry i sekunder",
    )

    # API-konfigurasjoner
    met_api_base_url: HttpUrl = Field(
        default="https://api.met.no/weatherapi",
        description="Base URL for Met.no API",
    )
    
    electricity_api_base_url: HttpUrl = Field(
        default="https://www.hvakosterstrommen.no/api/v1/prices",
        description="Base URL for strømpris API",
    )
    
    coingecko_api_base_url: HttpUrl = Field(
        default="https://api.coingecko.com/api/v3",
        description="Base URL for CoinGecko API",
    )

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        """Validerer og normaliserer bynavn."""
        return v.strip().title()

    @field_validator("data_dir")
    @classmethod
    def validate_data_dir(cls, v: Path) -> Path:
        """Validerer at datamappe eksisterer."""
        if not v.exists():
            raise ValueError(f"Datamappe eksisterer ikke: {v}")
        return v

    @model_validator(mode="after")
    def validate_settings(self) -> "Settings":
        """Validerer innstillinger etter initialisering."""
        if self.debug:
            # I debug-modus, bruk kortere cache
            object.__setattr__(self, "cache_ttl", min(self.cache_ttl, 60))
        return self

    @property
    def has_ai(self) -> bool:
        """Sjekker om AI-funksjoner er tilgjengelig."""
        return self.groq_api_key is not None


@lru_cache
def get_settings() -> Settings:
    """
    Henter cached innstillinger.
    
    Returns:
        Applikasjonsinnstillinger
    """
    return Settings()
