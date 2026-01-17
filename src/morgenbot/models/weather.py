"""
Datamodeller for værdata.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class WeatherCondition(BaseModel):
    """Værtilstand."""
    
    symbol_code: str = Field(..., description="Yr symbol kode")
    symbol_text: str = Field(..., description="Beskrivelse av været")
    icon: str = Field(..., description="Emoji-ikon")


class CurrentWeather(BaseModel):
    """Nåværende vær."""
    
    temperature: float = Field(..., description="Temperatur i Celsius")
    wind_speed: float = Field(..., ge=0, description="Vindhastighet i m/s")
    wind_direction: Optional[float] = Field(None, ge=0, lt=360, description="Vindretning i grader")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Relativ fuktighet i prosent")
    pressure: Optional[float] = Field(None, description="Lufttrykk ved havnivå i hPa")
    condition: WeatherCondition = Field(..., description="Værtilstand")
    clothing_advice: str = Field(..., description="Klesanbefaling")
    timestamp: datetime = Field(default_factory=datetime.now, description="Tidspunkt for måling")

    @computed_field
    @property
    def feels_like(self) -> float:
        """Beregner 'føles som' temperatur."""
        from morgenbot.utils.calculations import calculate_wind_chill
        return round(calculate_wind_chill(self.temperature, self.wind_speed), 1)

    @computed_field
    @property
    def is_cold(self) -> bool:
        """Sjekker om det er kaldt."""
        return self.temperature < 5

    @computed_field
    @property
    def is_warm(self) -> bool:
        """Sjekker om det er varmt."""
        return self.temperature > 20


class SunTimes(BaseModel):
    """Soloppgang og solnedgang."""
    
    sunrise: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Soloppgang (HH:MM)")
    sunset: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Solnedgang (HH:MM)")
    daylight_hours: int = Field(..., ge=0, le=24, description="Timer med dagslys")
    daylight_minutes: int = Field(..., ge=0, lt=60, description="Minutter med dagslys")
    
    @computed_field
    @property
    def total_daylight_minutes(self) -> int:
        """Totalt antall minutter med dagslys."""
        return self.daylight_hours * 60 + self.daylight_minutes

    @computed_field
    @property
    def daylight_formatted(self) -> str:
        """Formatert dagslystid."""
        return f"{self.daylight_hours}t {self.daylight_minutes}min"


class WeatherData(BaseModel):
    """Komplett værdata."""
    
    city: str = Field(..., description="By")
    current: CurrentWeather = Field(..., description="Nåværende vær")
    sun: Optional[SunTimes] = Field(None, description="Sol-tider")
    
    class Config:
        frozen = True
