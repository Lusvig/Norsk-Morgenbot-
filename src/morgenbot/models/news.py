"""
Datamodeller for nyheter.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class NewsCategory(StrEnum):
    """Nyhetskategorier."""
    
    TOP = "top"
    WORLD = "world"
    SPORT = "sport"
    CULTURE = "culture"
    TECH = "tech"
    BUSINESS = "business"


class NewsItem(BaseModel):
    """En nyhetssak."""
    
    title: str
    link: str
    source: str
    category: NewsCategory


class NewsData(BaseModel):
    """Samling av nyheter."""
    
    top: list[NewsItem]
    world: list[NewsItem]
    sport: list[NewsItem]
    culture: list[NewsItem]
    tech: list[NewsItem]

    def all_news(self) -> list[NewsItem]:
        """Returnerer alle nyheter."""
        return self.top + self.world + self.sport + self.culture + self.tech
