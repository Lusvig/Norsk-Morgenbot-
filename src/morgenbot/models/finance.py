"""
Datamodeller for finansdata.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class TrendDirection(StrEnum):
    """Trendretning."""
    
    UP = "up"
    DOWN = "down"
    UNCHANGED = "unchanged"


class StockQuote(BaseModel):
    """Aksjekurs."""
    
    symbol: str = Field(..., description="Ticker-symbol")
    name: str = Field(..., description="Selskapsnavn")
    price: Decimal = Field(..., description="Nåværende pris")
    change_percent: float = Field(..., description="Prosentvis endring")
    currency: str = Field(default="NOK", description="Valuta")
    timestamp: datetime = Field(default_factory=datetime.now)

    @computed_field
    @property
    def trend(self) -> TrendDirection:
        """Bestemmer trendretning."""
        if self.change_percent > 0.01:
            return TrendDirection.UP
        elif self.change_percent < -0.01:
            return TrendDirection.DOWN
        return TrendDirection.UNCHANGED

    @computed_field
    @property
    def trend_emoji(self) -> str:
        """Emoji for trend."""
        return "📈" if self.trend == TrendDirection.UP else "📉" if self.trend == TrendDirection.DOWN else "➡️"

    @computed_field
    @property
    def change_formatted(self) -> str:
        """Formatert prosentendring."""
        sign = "+" if self.change_percent >= 0 else ""
        return f"{sign}{self.change_percent:.2f}%"


class CurrencyRate(BaseModel):
    """Valutakurs."""
    
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(default="NOK", min_length=3, max_length=3)
    rate: Decimal = Field(..., gt=0)
    emoji: str = Field(default="💱")

    @computed_field
    @property
    def pair(self) -> str:
        """Valutapar som streng."""
        return f"{self.from_currency}/{self.to_currency}"


class CryptoPrice(BaseModel):
    """Kryptovaluta-pris."""
    
    id: str = Field(..., description="CoinGecko ID")
    name: str = Field(..., description="Navn")
    symbol: str = Field(..., description="Symbol/ticker")
    price_nok: Decimal = Field(..., ge=0)
    price_usd: Optional[Decimal] = Field(None, ge=0)
    change_24h: float = Field(..., description="24t endring i prosent")
    emoji: str = Field(default="🪙")

    @computed_field
    @property
    def trend_emoji(self) -> str:
        """Trend-emoji."""
        return "📈" if self.change_24h >= 0 else "📉"

    @computed_field
    @property
    def change_formatted(self) -> str:
        """Formatert endring."""
        sign = "+" if self.change_24h >= 0 else ""
        return f"{sign}{self.change_24h:.1f}%"


class ElectricityPrice(BaseModel):
    """Strømpris."""
    
    zone: str = Field(..., description="Prissone")
    current_price: Optional[float] = Field(None, ge=0, description="Nåværende pris i øre/kWh")
    average_price: float = Field(..., ge=0, description="Gjennomsnittspris i øre/kWh")
    cheapest_hour: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    cheapest_price: float = Field(..., ge=0)
    most_expensive_hour: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    most_expensive_price: float = Field(..., ge=0)

    @computed_field
    @property
    def price_level(self) -> str:
        """Prisnivå-indikator."""
        if self.current_price is None:
            return "🟡"
        if self.current_price < 50:
            return "🟢"
        if self.current_price < 100:
            return "🟡"
        return "🔴"


class FinanceData(BaseModel):
    """Samlet finansdata."""
    
    stocks: list[StockQuote] = Field(default_factory=list)
    currencies: list[CurrencyRate] = Field(default_factory=list)
    crypto: list[CryptoPrice] = Field(default_factory=list)
    electricity: Optional[ElectricityPrice] = None
    timestamp: datetime = Field(default_factory=datetime.now)
