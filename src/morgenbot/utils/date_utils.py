"""
Hjelpefunksjoner for dato og tid.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from morgenbot.config.constants import MONTHS, WEEKDAYS


def format_norwegian_date(d: Optional[date] = None) -> str:
    """
    Formaterer dato på norsk.
    
    Args:
        d: Dato å formatere, eller None for i dag
        
    Returns:
        Formatert dato, f.eks. "Mandag 15. januar 2024"
    """
    if d is None:
        d = date.today()
    
    weekday = WEEKDAYS[d.weekday()].capitalize()
    month = MONTHS[d.month - 1]
    
    return f"{weekday} {d.day}. {month} {d.year}"


def format_norwegian_date_with_week(d: Optional[date] = None) -> str:
    """
    Formaterer dato med ukenummer.
    
    Args:
        d: Dato å formatere, eller None for i dag
        
    Returns:
        Formatert dato med ukenummer
    """
    if d is None:
        d = date.today()
    
    base = format_norwegian_date(d)
    week = d.isocalendar()[1]
    
    return f"{base} (Uke {week})"


def days_until(target: date) -> int:
    """
    Beregner dager til en dato.
    
    Args:
        target: Måldato
        
    Returns:
        Antall dager (negativt hvis i fortiden)
    """
    return (target - date.today()).days


def format_countdown(days: int, event_name: str) -> str:
    """
    Formaterer nedtelling til en hendelse.
    
    Args:
        days: Antall dager
        event_name: Navn på hendelsen
        
    Returns:
        Formatert nedtellingsstreng
    """
    if days == 0:
        return f"🎉 **I DAG: {event_name}!**"
    elif days == 1:
        return f"📅 **I morgen:** {event_name}"
    elif days < 0:
        return f"📅 {event_name} var for {abs(days)} dager siden"
    else:
        return f"📅 **{event_name}** om {days} dager"


def get_greeting_time() -> str:
    """
    Returnerer passende hilsningsord basert på tid på døgnet.
    
    Returns:
        Hilsningsord
    """
    hour = datetime.now().hour
    
    if 5 <= hour < 10:
        return "God morgen"
    elif 10 <= hour < 12:
        return "God formiddag"
    elif 12 <= hour < 17:
        return "God ettermiddag"
    elif 17 <= hour < 21:
        return "God kveld"
    else:
        return "God natt"


def is_weekend() -> bool:
    """Sjekker om det er helg."""
    return date.today().weekday() >= 5


def is_weekday() -> bool:
    """Sjekker om det er hverdag."""
    return date.today().weekday() < 5
