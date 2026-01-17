"""
Tjeneste for henting av værdata fra Meteorologisk institutt.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from morgenbot.data.loader import DataLoader
from morgenbot.models.weather import CurrentWeather, WeatherCondition, WeatherData
from morgenbot.services.base import CachedService
from morgenbot.utils.calculations import get_clothing_advice

if TYPE_CHECKING:
    from morgenbot.config.settings import Settings


class WeatherService(CachedService[WeatherData]):
    """
    Henter værdata fra Met.no API.
    
    Implementerer LocationForecast 2.0 API.
    """

    def __init__(self, settings: "Settings") -> None:
        super().__init__(settings)
        self.base_url = str(settings.met_api_base_url)
        self.data_loader = DataLoader(settings.data_dir)
        self._weather_symbols = self.data_loader.load_weather_symbols()
        self._cities = self.data_loader.load_cities()

    async def get_weather(self, city: str) -> WeatherData | None:
        """
        Henter værdata for en by.
        
        Args:
            city: Navn på byen
            
        Returns:
            Værdata, eller None ved feil
        """
        cache_key = f"weather:{city}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            city_data = self._get_city_data(city)
            raw_data = await self._fetch_weather(city_data["lat"], city_data["lon"])
            weather = self._parse_weather(raw_data, city)
            
            self._set_cached(cache_key, weather)
            return weather

        except Exception as e:
            self.logger.error("weather_fetch_failed", city=city, error=str(e))
            return None

    async def fetch(self) -> WeatherData | None:
        """Henter vær for standard by."""
        return await self.get_weather(self.settings.city)

    def _get_city_data(self, city: str) -> dict[str, Any]:
        """Henter koordinater for en by."""
        city_lower = city.lower()
        for city_name, data in self._cities.items():
            if city_name.lower() == city_lower:
                return data
        
        self.logger.warning("city_not_found", city=city, fallback="Moss")
        return self._cities.get("Moss", {"lat": 59.43, "lon": 10.66})

    async def _fetch_weather(self, lat: float, lon: float) -> dict[str, Any]:
        """Henter rå værdata fra API."""
        url = f"{self.base_url}/locationforecast/2.0/compact"
        params = {"lat": lat, "lon": lon}
        return await self._get_json(url, params=params)

    def _parse_weather(self, data: dict[str, Any], city: str) -> WeatherData:
        """Parser værdata fra API-respons."""
        timeseries = data["properties"]["timeseries"][0]
        instant = timeseries["data"]["instant"]["details"]
        
        # Hent værsymbol
        next_data = timeseries["data"]
        if "next_1_hours" in next_data:
            symbol_code = next_data["next_1_hours"]["summary"]["symbol_code"]
        elif "next_6_hours" in next_data:
            symbol_code = next_data["next_6_hours"]["summary"]["symbol_code"]
        else:
            symbol_code = "cloudy"

        symbol_base = symbol_code.split("_")[0]
        symbol_info = self._weather_symbols.get(symbol_base, {})
        
        temperature = instant["air_temperature"]
        wind_speed = instant["wind_speed"]
        
        condition = WeatherCondition(
            symbol_code=symbol_code,
            symbol_text=symbol_info.get("text", symbol_code),
            icon=symbol_info.get("icon", "❓"),
        )
        
        current = CurrentWeather(
            temperature=temperature,
            wind_speed=wind_speed,
            wind_direction=instant.get("wind_from_direction"),
            humidity=instant.get("relative_humidity"),
            pressure=instant.get("air_pressure_at_sea_level"),
            condition=condition,
            clothing_advice=get_clothing_advice(temperature, symbol_code),
        )
        
        return WeatherData(city=city, current=current)
