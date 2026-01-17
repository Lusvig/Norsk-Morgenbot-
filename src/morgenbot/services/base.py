"""
Base-klasse for alle tjenester.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

if TYPE_CHECKING:
    from morgenbot.config.settings import Settings


logger = structlog.get_logger(__name__)

T = TypeVar("T")


class BaseService(ABC, Generic[T]):
    """
    Abstrakt base-klasse for tjenester.
    
    Gir felles funksjonalitet som HTTP-klient, retry-logikk og logging.
    """

    def __init__(self, settings: "Settings") -> None:
        """
        Initialiserer tjenesten.
        
        Args:
            settings: Applikasjonsinnstillinger
        """
        self.settings = settings
        self._client: httpx.AsyncClient | None = None
        self.logger = logger.bind(service=self.__class__.__name__)

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-initialisert HTTP-klient."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.settings.request_timeout,
                headers={"User-Agent": self.settings.user_agent},
            )
        return self._client

    async def close(self) -> None:
        """Lukker HTTP-klienten."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _get(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Utfører GET-forespørsel med retry.
        
        Args:
            url: URL å hente
            **kwargs: Ekstra argumenter til httpx
            
        Returns:
            HTTP-respons
        """
        self.logger.debug("http_get", url=url)
        response = await self.client.get(url, **kwargs)
        response.raise_for_status()
        return response

    async def _get_json(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """
        Henter JSON fra URL.
        
        Args:
            url: URL å hente
            **kwargs: Ekstra argumenter til httpx
            
        Returns:
            JSON-data som dict
        """
        response = await self._get(url, **kwargs)
        return response.json()

    @abstractmethod
    async def fetch(self) -> T | None:
        """
        Henter data fra tjenesten.
        
        Returns:
            Data fra tjenesten, eller None ved feil
        """
        ...


class CachedService(BaseService[T]):
    """
    Tjeneste med caching.
    """

    def __init__(self, settings: "Settings") -> None:
        super().__init__(settings)
        self._cache: dict[str, tuple[float, T]] = {}

    def _get_cached(self, key: str) -> T | None:
        """Henter cached verdi hvis gyldig."""
        import time
        
        if key in self._cache:
            cached_time, value = self._cache[key]
            if time.time() - cached_time < self.settings.cache_ttl:
                self.logger.debug("cache_hit", key=key)
                return value
            del self._cache[key]
        return None

    def _set_cached(self, key: str, value: T) -> None:
        """Lagrer verdi i cache."""
        import time
        
        self._cache[key] = (time.time(), value)
        self.logger.debug("cache_set", key=key)
