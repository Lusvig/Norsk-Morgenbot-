"""
Tjeneste for henting av strømpriser.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from morgenbot.data.loader import DataLoader
from morgenbot.models.finance import ElectricityPrice
from morgenbot.services.base import CachedService

if TYPE_CHECKING:
    from morgenbot.config.settings import Settings


class ElectricityService(CachedService[ElectricityPrice]):
    """
    Henter strømpriser fra hvakosterstrommen.no.
    """

    def __init__(self, settings: "Settings") -> None:
        super().__init__(settings)
        self.base_url = str(settings.electricity_api_base_url)
        self.data_loader = DataLoader(settings.data_dir)
        self._cities = self.data_loader.load_cities()

    async def get_prices(self, city: str) -> ElectricityPrice | None:
        """
        Henter strømpriser for en by.
        
        Args:
            city: Navn på byen
            
        Returns:
            Strømprisdata, eller None ved feil
        """
        today = datetime.now().strftime("%Y-%m-%d")
        cache_key = f"electricity:{city}:{today}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            zone = self._get_power_zone(city)
            raw_data = await self._fetch_prices(zone)
            
            if not raw_data:
                return None
            
            prices = self._parse_prices(raw_data, zone)
            self._set_cached(cache_key, prices)
            return prices

        except Exception as e:
            self.logger.error("electricity_fetch_failed", city=city, error=str(e))
            return None

    async def fetch(self) -> ElectricityPrice | None:
        """Henter strømpriser for standard by."""
        return await self.get_prices(self.settings.city)

    def _get_power_zone(self, city: str) -> str:
        """Finner strømsone for en by."""
        city_data = self._cities.get(city, {})
        return city_data.get("power_zone", "NO1")

    async def _fetch_prices(self, zone: str) -> list[dict[str, Any]]:
        """Henter rå prisdata fra API."""
        date_path = datetime.now().strftime("%Y/%m-%d")
        url = f"{self.base_url}/{date_path}_{zone}.json"
        
        return await self._get_json(url)

    def _parse_prices(
        self, data: list[dict[str, Any]], zone: str
    ) -> ElectricityPrice:
        """Parser prisdata fra API."""
        # Finn nåværende pris
        current_hour = datetime.now().hour
        current_price = None
        
        for item in data:
            if f"T{current_hour:02d}" in item["time_start"]:
                current_price = item["NOK_per_kWh"] * 100  # Konverter til øre
                break
        
        # Finn billigst og dyrest
        cheapest = min(data, key=lambda x: x["NOK_per_kWh"])
        expensive = max(data, key=lambda x: x["NOK_per_kWh"])
        
        # Beregn gjennomsnitt
        avg = sum(item["NOK_per_kWh"] for item in data) / len(data) * 100
        
        return ElectricityPrice(
            zone=zone,
            current_price=round(current_price, 1) if current_price else None,
            average_price=round(avg, 1),
            cheapest_hour=cheapest["time_start"][11:16],
            cheapest_price=round(cheapest["NOK_per_kWh"] * 100, 1),
            most_expensive_hour=expensive["time_start"][11:16],
            most_expensive_price=round(expensive["NOK_per_kWh"] * 100, 1),
        )
