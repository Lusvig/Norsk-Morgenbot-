"""
Konstanter og statiske verdier for Morgenbot.

Inneholder uforanderlige verdier som brukes på tvers av applikasjonen.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class PowerZone(StrEnum):
    """Norske strømprissoner."""
    
    NO1 = "NO1"  # Øst-Norge
    NO2 = "NO2"  # Sør-Norge
    NO3 = "NO3"  # Midt-Norge
    NO4 = "NO4"  # Nord-Norge
    NO5 = "NO5"  # Vest-Norge


class NewsCategory(StrEnum):
    """Nyhetskategorier."""
    
    TOP = "top"
    WORLD = "world"
    SPORT = "sport"
    CULTURE = "culture"
    TECH = "tech"
    BUSINESS = "business"


class ContentType(StrEnum):
    """Typer underholdningsinnhold."""
    
    JOKE = "joke"
    PROVERB = "proverb"
    QUOTE = "quote"
    FUN_FACT = "fun_fact"


# Norske dager og måneder
WEEKDAYS: Final[tuple[str, ...]] = (
    "mandag",
    "tirsdag",
    "onsdag",
    "torsdag",
    "fredag",
    "lørdag",
    "søndag",
)

MONTHS: Final[tuple[str, ...]] = (
    "januar",
    "februar",
    "mars",
    "april",
    "mai",
    "juni",
    "juli",
    "august",
    "september",
    "oktober",
    "november",
    "desember",
)

# Discord embed farger (hex)
WEEKDAY_COLORS: Final[dict[int, int]] = {
    0: 0x3498DB,  # Mandag - blå
    1: 0x2ECC71,  # Tirsdag - grønn
    2: 0x9B59B6,  # Onsdag - lilla
    3: 0xE67E22,  # Torsdag - oransje
    4: 0xE74C3C,  # Fredag - rød
    5: 0xF39C12,  # Lørdag - gul
    6: 0x1ABC9C,  # Søndag - turkis
}

# Strømpris terskelverider (øre/kWh)
ELECTRICITY_THRESHOLDS: Final[dict[str, int]] = {
    "low": 50,
    "medium": 100,
    "high": 200,
}

# API Rate limits
RATE_LIMITS: Final[dict[str, int]] = {
    "met_no": 20,  # per minutt
    "coingecko": 10,  # per minutt
    "yahoo_finance": 100,  # per time
}

# Cryptocurrency symboler
CRYPTO_SYMBOLS: Final[dict[str, str]] = {
    "bitcoin": "₿",
    "ethereum": "Ξ",
    "solana": "◎",
    "dogecoin": "🐕",
    "cardano": "₳",
    "ripple": "✕",
    "polkadot": "●",
}

# Klesanbefaling temperaturgrenser
CLOTHING_THRESHOLDS: Final[list[tuple[float, str]]] = [
    (-15.0, "🥶 EKSTREMT kaldt! Full vinterutrustning, begrens tid ute"),
    (-10.0, "🧥 Veldig kaldt! Boblejakke, lue, votter, skjerf og ullundertøy"),
    (0.0, "🧥 Kaldt! Varm jakke, lue og hansker anbefales"),
    (5.0, "🧥 Kjølig. Jakke og lag-på-lag"),
    (10.0, "🧥 Friskt. Lett jakke eller tykk genser"),
    (15.0, "👕 Behagelig. Genser eller lett jakke"),
    (20.0, "👕 Fint vær! T-skjorte og lett bukse"),
    (25.0, "☀️ Varmt! T-skjorte og shorts"),
]

DEFAULT_CLOTHING_ADVICE: Final[str] = "🥵 Veldig varmt! Lett, luftig klær. Husk solkrem!"

# News RSS feeds
NEWS_FEEDS: Final[dict[str, list[str]]] = {
    "top": [
        "https://www.nrk.no/toppsaker.rss",
        "https://www.vg.no/rss/feed/?categories=1069&limit=10",
    ],
    "world": [
        "https://www.nrk.no/verden/toppsaker.rss",
    ],
    "sport": [
        "https://www.nrk.no/sport/toppsaker.rss",
        "https://www.vg.no/rss/feed/?categories=1070&limit=5",
    ],
    "culture": [
        "https://www.nrk.no/kultur/toppsaker.rss",
    ],
    "tech": [
        "https://www.nrk.no/viten/toppsaker.rss",
    ],
}

# Standard aksjer å følge
DEFAULT_STOCKS: Final[list[tuple[str, str]]] = [
    ("^OSEAX", "Oslo Børs"),
    ("EQNR.OL", "Equinor"),
    ("DNB.OL", "DNB"),
    ("TEL.OL", "Telenor"),
    ("MOWI.OL", "Mowi"),
    ("NHY.OL", "Norsk Hydro"),
    ("YAR.OL", "Yara"),
]

# Standard kryptovalutaer
DEFAULT_CRYPTOS: Final[list[str]] = [
    "bitcoin",
    "ethereum",
    "solana",
    "dogecoin",
    "cardano",
]

# Valutapar
CURRENCY_PAIRS: Final[list[tuple[str, str, str]]] = [
    ("USD", "💵", "USD/NOK"),
    ("EUR", "💶", "EUR/NOK"),
    ("SEK", "🇸🇪", "SEK/NOK"),
    ("GBP", "💷", "GBP/NOK"),
]
