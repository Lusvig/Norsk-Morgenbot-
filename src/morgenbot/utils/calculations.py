"""
Beregningsfunksjoner.
"""

from __future__ import annotations

from morgenbot.config.constants import CLOTHING_THRESHOLDS, DEFAULT_CLOTHING_ADVICE


def calculate_wind_chill(temperature: float, wind_speed: float) -> float:
    """
    Beregner 'føles som' temperatur basert på vind.
    
    Bruker den kanadiske vindkjølings-formelen.
    
    Args:
        temperature: Temperatur i Celsius
        wind_speed: Vindhastighet i m/s
        
    Returns:
        Følt temperatur i Celsius
    """
    if wind_speed <= 0 or temperature >= 10:
        return temperature
    
    # Konverter til km/h for formelen
    wind_kmh = wind_speed * 3.6
    
    # Vindkjølingsformel
    wind_chill = (
        13.12
        + 0.6215 * temperature
        - 11.37 * (wind_kmh ** 0.16)
        + 0.3965 * temperature * (wind_kmh ** 0.16)
    )
    
    return round(wind_chill, 1)


def get_clothing_advice(temperature: float, weather_code: str) -> str:
    """
    Gir klesanbefaling basert på vær.
    
    Args:
        temperature: Temperatur i Celsius
        weather_code: Værkode fra API
        
    Returns:
        Klesanbefaling som streng
    """
    # Finn base-anbefaling basert på temperatur
    advice = DEFAULT_CLOTHING_ADVICE
    for threshold, text in CLOTHING_THRESHOLDS:
        if temperature < threshold:
            advice = text
            break
    
    # Legg til værbetingelser
    weather_lower = weather_code.lower()
    
    if "rain" in weather_lower or "sleet" in weather_lower:
        advice += " 🌂 Ta med paraply!"
    if "snow" in weather_lower:
        advice += " ❄️ Vær obs på glatte veier!"
    if "thunder" in weather_lower:
        advice += " ⛈️ Vær forsiktig ute!"
    
    return advice


def calculate_daylight(sunrise_minutes: int, sunset_minutes: int) -> tuple[int, int]:
    """
    Beregner dagslystid.
    
    Args:
        sunrise_minutes: Soloppgang i minutter fra midnatt
        sunset_minutes: Solnedgang i minutter fra midnatt
        
    Returns:
        Tuple med (timer, minutter) dagslys
    """
    total_minutes = sunset_minutes - sunrise_minutes
    if total_minutes < 0:
        total_minutes += 24 * 60  # Håndter over midnatt
    
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    return hours, minutes


def format_large_number(number: float, decimals: int = 2) -> str:
    """
    Formaterer store tall med tusenskilletegn.
    
    Args:
        number: Tall å formatere
        decimals: Antall desimaler
        
    Returns:
        Formatert streng
    """
    if number >= 1_000_000:
        return f"{number / 1_000_000:,.{decimals}f}M"
    elif number >= 1_000:
        return f"{number / 1_000:,.{decimals}f}K"
    else:
        return f"{number:,.{decimals}f}"
