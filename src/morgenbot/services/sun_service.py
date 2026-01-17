"""
Tjeneste for henting av sol-data fra Meteorologisk institutt.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from morgenbot.data.loader import DataLoader
from morgenbot.models.weather import SunTimes
from morgenbot.services.base import CachedService

if TYPE_CHECKING:
    from morgenbot.config.settings import Settings


class SunService(CachedService[SunTimes]):
    """
    Henter soloppgang og solnedgang fra Met.no Sunrise API.
    """

    def __init__(self, settings: "Settings") -> None:
        super().__init__(settings)
        self.base_url = str(settings.met_api_base_url)
        self.data_loader = DataLoader(settings.data_dir)
        self._cities = self.data_loader.load_cities()

    async def get_sun_times(self, city: str) -> SunTimes | None:
        """
        Henter sol-tider for en by.
        
        Args:
            city: Navn på byen
            
        Returns:
            Sol-data, eller None ved feil
        """
        cache_key = f"sun:{city}:{datetime.now().date()}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            city_data = self._get_city_data(city)
            raw_data = await self._fetch_sun_times(
                city_data["lat"], city_data["lon"]
            )
            sun_times = self._parse_sun_times(raw_data)
            
            self._set_cached(cache_key, sun_times)
            return sun_times

        except Exception as e:
            self.logger.error("sun_fetch_failed", city=city, error=str(e))
            return None

    async def fetch(self) -> SunTimes | None:
        """Henter sol-tider for standard by."""
        return await self.get_sun_times(self.settings.city)

    def _get_city_data(self, city: str) -> dict[str, Any]:
        """Henter koordinater for en by."""
        city_lower = city.lower()
        for city_name, data in self._cities.items():
            if city_name.lower() == city_lower:
                return data
        return self._cities.get("Moss", {"lat": 59.43, "lon": 10.66})

    async def _fetch_sun_times(self, lat: float, lon: float) -> dict[str, Any]:
        """Henter rå sol-data fra API."""
        today = datetime.now().strftime("%Y-%m-%d")
        url = f"{self.base_url}/sunrise/3.0/sun"
        params = {
            "lat": lat,
            "lon": lon,
            "date": today,
            "offset": "+01:00",
        }
        return await self._get_json(url, params=params)

    def _parse_sun_times(self, data: dict[str, Any]) -> SunTimes:
        """Parser sol-data fra API-respons."""
        props = data["properties"]
        
        sunrise_str = props["sunrise"]["time"]
        sunset_str = props["sunset"]["time"]
        
        sunrise_dt = datetime.fromisoformat(sunrise_str.replace("Z", "+00:00"))
        sunset_dt = datetime.fromisoformat(sunset_str.replace("Z", "+00:00"))
        
        # Beregn dagslys
        daylight = sunset_dt - sunrise_dt
        hours = daylight.seconds // 3600
        minutes = (daylight.seconds % 3600) // 60
        
        return SunTimes(
            sunrise=sunrise_dt.strftime("%H:%M"),
            sunset=sunset_dt.strftime("%H:%M"),
            daylight_hours=hours,
            daylight_minutes=minutes,
        )
