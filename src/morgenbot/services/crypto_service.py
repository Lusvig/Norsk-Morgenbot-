"""
Tjeneste for henting av kryptovaluta-priser.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from morgenbot.config.constants import CRYPTO_SYMBOLS, DEFAULT_CRYPTOS
from morgenbot.models.finance import CryptoPrice
from morgenbot.services.base import CachedService

if TYPE_CHECKING:
    from morgenbot.config.settings import Settings


class CryptoService(CachedService[list[CryptoPrice]]):
    """
    Henter kryptovaluta-priser fra CoinGecko.
    """

    def __init__(self, settings: "Settings") -> None:
        super().__init__(settings)
        self.base_url = str(settings.coingecko_api_base_url)
        self.coins = DEFAULT_CRYPTOS

    async def get_prices(self) -> list[CryptoPrice] | None:
        """
        Henter krypto-priser.
        
        Returns:
            Liste med krypto-priser, eller None ved feil
        """
        cache_key = "crypto:prices"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            coins_param = ",".join(self.coins)
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": coins_param,
                "vs_currencies": "nok,usd",
                "include_24hr_change": "true",
            }
            
            data = await self._get_json(url, params=params)
            prices = self._parse_prices(data)
            
            self._set_cached(cache_key, prices)
            return prices

        except Exception as e:
            self.logger.error("crypto_fetch_failed", error=str(e))
            return None

    async def fetch(self) -> list[CryptoPrice] | None:
        """Henter alle krypto-priser."""
        return await self.get_prices()

    def _parse_prices(self, data: dict) -> list[CryptoPrice]:
        """Parser krypto-data fra API."""
        prices = []
        
        for coin in self.coins:
            if coin not in data:
                continue
            
            coin_data = data[coin]
            prices.append(
                CryptoPrice(
                    id=coin,
                    name=coin.capitalize(),
                    symbol=coin[:3].upper(),
                    price_nok=Decimal(str(coin_data.get("nok", 0))),
                    price_usd=Decimal(str(coin_data.get("usd", 0))),
                    change_24h=coin_data.get("nok_24h_change", 0),
                    emoji=CRYPTO_SYMBOLS.get(coin, "🪙"),
                )
            )
        
        return prices
