"""
Tjeneste for henting av aksje- og valutadata.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from morgenbot.config.constants import CURRENCY_PAIRS, DEFAULT_STOCKS
from morgenbot.models.finance import CurrencyRate, FinanceData, StockQuote
from morgenbot.services.base import CachedService

if TYPE_CHECKING:
    from morgenbot.config.settings import Settings


class FinanceService(CachedService[FinanceData]):
    """
    Henter aksje- og valutadata.
    """

    def __init__(self, settings: "Settings") -> None:
        super().__init__(settings)
        self.stocks = DEFAULT_STOCKS
        self.currency_pairs = CURRENCY_PAIRS

    async def get_stocks_and_currency(self) -> FinanceData | None:
        """
        Henter aksjer og valutakurser.
        
        Returns:
            Finansdata, eller None ved feil
        """
        cache_key = "finance:all"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            stocks = await self._fetch_stocks()
            currencies = await self._fetch_currencies()
            
            data = FinanceData(stocks=stocks, currencies=currencies)
            self._set_cached(cache_key, data)
            return data

        except Exception as e:
            self.logger.error("finance_fetch_failed", error=str(e))
            return None

    async def fetch(self) -> FinanceData | None:
        """Henter all finansdata."""
        return await self.get_stocks_and_currency()

    async def _fetch_stocks(self) -> list[StockQuote]:
        """Henter aksjekurser fra Yahoo Finance."""
        quotes = []
        
        for symbol, name in self.stocks:
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                data = await self._get_json(url)
                
                result = data.get("chart", {}).get("result", [])
                if not result:
                    continue
                
                meta = result[0].get("meta", {})
                current = meta.get("regularMarketPrice", 0)
                previous = meta.get("previousClose", 0)
                
                if previous > 0:
                    change = ((current - previous) / previous) * 100
                else:
                    change = 0.0
                
                quotes.append(
                    StockQuote(
                        symbol=symbol,
                        name=name,
                        price=Decimal(str(current)),
                        change_percent=change,
                    )
                )
                
            except Exception as e:
                self.logger.warning(
                    "stock_fetch_failed",
                    symbol=symbol,
                    error=str(e),
                )
        
        return quotes

    async def _fetch_currencies(self) -> list[CurrencyRate]:
        """Henter valutakurser."""
        try:
            url = "https://api.exchangerate-api.com/v4/latest/NOK"
            data = await self._get_json(url)
            rates = data.get("rates", {})
            
            currencies = []
            for currency, emoji, _ in self.currency_pairs:
                if currency in rates:
                    rate = 1 / rates[currency]
                    currencies.append(
                        CurrencyRate(
                            from_currency=currency,
                            rate=Decimal(str(round(rate, 4))),
                            emoji=emoji,
                        )
                    )
            
            return currencies
            
        except Exception as e:
            self.logger.error("currency_fetch_failed", error=str(e))
            return []
