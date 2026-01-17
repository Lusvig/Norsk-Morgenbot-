"""
Laster data fra JSON-filer.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import structlog


logger = structlog.get_logger(__name__)


class DataLoader:
    """
    Laster og cacher data fra JSON-filer.
    """

    def __init__(self, data_dir: Path) -> None:
        """
        Initialiserer DataLoader.
        
        Args:
            data_dir: Mappe med datafiler
        """
        self.data_dir = data_dir
        self.logger = logger.bind(component="DataLoader")

    def _load_json(self, filename: str) -> dict[str, Any]:
        """
        Laster JSON-fil.
        
        Args:
            filename: Filnavn (uten sti)
            
        Returns:
            Data fra filen
        """
        filepath = self.data_dir / filename
        
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
                self.logger.debug("file_loaded", filename=filename)
                return data
        except FileNotFoundError:
            self.logger.error("file_not_found", filename=filename)
            return {}
        except json.JSONDecodeError as e:
            self.logger.error("json_decode_error", filename=filename, error=str(e))
            return {}

    @lru_cache(maxsize=1)
    def load_cities(self) -> dict[str, dict[str, Any]]:
        """Laster bydata."""
        return self._load_json("cities.json")

    @lru_cache(maxsize=1)
    def load_holidays(self) -> dict[str, str]:
        """Laster helligdager."""
        return self._load_json("holidays.json")

    @lru_cache(maxsize=1)
    def load_vacations(self) -> dict[str, dict[str, str]]:
        """Laster ferieperioder."""
        return self._load_json("vacations.json")

    @lru_cache(maxsize=1)
    def load_events(self) -> dict[str, dict[str, str]]:
        """Laster store eventer."""
        return self._load_json("events.json")

    @lru_cache(maxsize=1)
    def load_name_days(self) -> dict[str, list[str]]:
        """Laster navnedager."""
        return self._load_json("name_days.json")

    @lru_cache(maxsize=1)
    def load_historical_events(self) -> dict[str, list[str]]:
        """Laster historiske hendelser."""
        return self._load_json("historical_events.json")

    @lru_cache(maxsize=1)
    def load_weather_symbols(self) -> dict[str, dict[str, str]]:
        """Laster værsymboler."""
        return self._load_json("weather_symbols.json")

    @lru_cache(maxsize=1)
    def load_jokes(self) -> list[str]:
        """Laster vitser."""
        data = self._load_json("jokes.json")
        return data.get("jokes", [])

    @lru_cache(maxsize=1)
    def load_proverbs(self) -> list[str]:
        """Laster ordtak."""
        data = self._load_json("proverbs.json")
        return data.get("proverbs", [])

    @lru_cache(maxsize=1)
    def load_quotes(self) -> list[str]:
        """Laster sitater."""
        data = self._load_json("quotes.json")
        return data.get("quotes", [])

    @lru_cache(maxsize=1)
    def load_fun_facts(self) -> list[str]:
        """Laster morsomme fakta."""
        data = self._load_json("fun_facts.json")
        return data.get("facts", [])

    def clear_cache(self) -> None:
        """Tømmer cache."""
        self.load_cities.cache_clear()
        self.load_holidays.cache_clear()
        self.load_vacations.cache_clear()
        self.load_events.cache_clear()
        self.load_name_days.cache_clear()
        self.load_historical_events.cache_clear()
        self.load_weather_symbols.cache_clear()
        self.load_jokes.cache_clear()
        self.load_proverbs.cache_clear()
        self.load_quotes.cache_clear()
        self.load_fun_facts.cache_clear()
