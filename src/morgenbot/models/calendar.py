"""
Datamodeller for kalender og datoer.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class Holiday(BaseModel):
    """Helligdag."""
    
    date: date
    name: str
    is_public_holiday: bool = True

    @computed_field
    @property
    def days_until(self) -> int:
        """Dager til helligdagen."""
        return (self.date - date.today()).days


class Vacation(BaseModel):
    """Ferieperiode."""
    
    name: str
    start_date: date
    end_date: date

    @computed_field
    @property
    def days_until_start(self) -> int:
        """Dager til ferien starter."""
        return (self.start_date - date.today()).days

    @computed_field
    @property
    def is_active(self) -> bool:
        """Sjekker om ferien er aktiv."""
        today = date.today()
        return self.start_date <= today <= self.end_date


class Event(BaseModel):
    """Stor begivenhet."""
    
    date: date
    name: str
    emoji: str
    description: Optional[str] = None

    @computed_field
    @property
    def days_until(self) -> int:
        """Dager til eventet."""
        return (self.date - date.today()).days


class HistoricalEvent(BaseModel):
    """Historisk hendelse."""
    
    year: Optional[int] = None
    description: str


class NameDay(BaseModel):
    """Navnedag."""
    
    date: str = Field(..., pattern=r"^\d{2}-\d{2}$")
    names: list[str]


class CalendarData(BaseModel):
    """Samlet kalenderdata."""
    
    today: date = Field(default_factory=date.today)
    weekday: int = Field(..., ge=0, le=6)
    week_number: int = Field(..., ge=1, le=53)
    next_holiday: Optional[Holiday] = None
    next_vacation: Optional[Vacation] = None
    next_event: Optional[Event] = None
    name_days: list[str] = Field(default_factory=list)
    historical_events: list[HistoricalEvent] = Field(default_factory=list)

    @computed_field
    @property
    def is_weekend(self) -> bool:
        """Sjekker om det er helg."""
        return self.weekday >= 5

    @classmethod
    def for_today(cls) -> "CalendarData":
        """Oppretter kalenderdata for i dag."""
        today = date.today()
        return cls(
            today=today,
            weekday=today.weekday(),
            week_number=today.isocalendar()[1],
        )
