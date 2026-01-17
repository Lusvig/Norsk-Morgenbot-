"""
Tjeneste for henting av nyheter fra RSS-feeds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import feedparser
import structlog

from morgenbot.config.constants import NEWS_FEEDS
from morgenbot.models.news import NewsCategory, NewsData, NewsItem
from morgenbot.services.base import CachedService

if TYPE_CHECKING:
    from morgenbot.config.settings import Settings


logger = structlog.get_logger(__name__)


class NewsService(CachedService[NewsData]):
    """
    Henter nyheter fra norske RSS-feeds.
    """

    def __init__(self, settings: "Settings") -> None:
        super().__init__(settings)
        self.feeds = NEWS_FEEDS
        self.max_items_per_category = 5

    async def get_news(self) -> NewsData | None:
        """
        Henter nyheter fra alle kategorier.
        
        Returns:
            Nyhetsdata, eller None ved feil
        """
        cache_key = "news:all"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            news = NewsData(
                top=await self._fetch_category(NewsCategory.TOP),
                world=await self._fetch_category(NewsCategory.WORLD),
                sport=await self._fetch_category(NewsCategory.SPORT),
                culture=await self._fetch_category(NewsCategory.CULTURE),
                tech=await self._fetch_category(NewsCategory.TECH),
            )
            
            self._set_cached(cache_key, news)
            return news

        except Exception as e:
            self.logger.error("news_fetch_failed", error=str(e))
            return None

    async def fetch(self) -> NewsData | None:
        """Henter alle nyheter."""
        return await self.get_news()

    async def _fetch_category(self, category: NewsCategory) -> list[NewsItem]:
        """Henter nyheter for en kategori."""
        items: list[NewsItem] = []
        feeds = self.feeds.get(category.value, [])
        
        for feed_url in feeds:
            try:
                feed_items = await self._parse_feed(feed_url, category)
                items.extend(feed_items)
            except Exception as e:
                self.logger.warning(
                    "feed_parse_failed",
                    url=feed_url,
                    error=str(e),
                )
        
        return items[: self.max_items_per_category]

    async def _parse_feed(
        self, url: str, category: NewsCategory
    ) -> list[NewsItem]:
        """Parser en RSS-feed."""
        # feedparser er synkron, men rask nok for vårt formål
        feed = feedparser.parse(url)
        source = "NRK" if "nrk.no" in url else "VG"
        
        items = []
        for entry in feed.entries[:3]:
            items.append(
                NewsItem(
                    title=entry.title,
                    link=entry.link,
                    source=source,
                    category=category,
                )
            )
        
        return items
