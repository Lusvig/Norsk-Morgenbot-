"""
Bygger komplette Discord-meldinger.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from morgenbot.builders.field_builders import (
    build_calendar_fields,
    build_entertainment_field,
    build_finance_fields,
    build_news_fields,
    build_weather_field,
)
from morgenbot.config.constants import WEEKDAY_COLORS
from morgenbot.models.discord import DiscordMessage, Embed, EmbedField, EmbedFooter
from morgenbot.utils.date_utils import format_norwegian_date_with_week

if TYPE_CHECKING:
    from morgenbot.config.settings import Settings


class MessageBuilder:
    """
    Bygger komplette Discord-meldinger fra innsamlet data.
    """

    def __init__(self, settings: "Settings") -> None:
        self.settings = settings

    def build(self, data: dict[str, Any]) -> DiscordMessage:
        """
        Bygger komplett Discord-melding.
        
        Args:
            data: All innsamlet data
            
        Returns:
            Ferdig formatert Discord-melding
        """
        now = datetime.now()
        
        # Bygg embed
        embed = Embed(
            title=f"☀️ God morgen! {format_norwegian_date_with_week()}",
            color=WEEKDAY_COLORS.get(now.weekday(), 0x5814FF),
            timestamp=now,
            footer=EmbedFooter(
                text=f"🤖 Morgenbot v{self.settings.version} | {self.settings.city}"
            ),
        )
        
        # Legg til AI-hilsning som beskrivelse
        if ai_greeting := data.get("ai_greeting"):
            embed.description = ai_greeting
        
        # Bygg og legg til alle fields
        fields = []
        
        # Vær
        if weather := data.get("weather"):
            sun = data.get("sun")
            weather_field = build_weather_field(weather, sun, self.settings.city)
            if weather_field:
                fields.append(weather_field)
        
        # Strømpris
        if electricity := data.get("electricity"):
            from morgenbot.builders.field_builders.finance_field import (
                build_electricity_field,
            )
            elec_field = build_electricity_field(electricity)
            if elec_field:
                fields.append(elec_field)
        
        # Nyheter
        if news := data.get("news"):
            news_fields = build_news_fields(news)
            fields.extend(news_fields)
        
        # Finans
        if finance := data.get("finance"):
            finance_fields = build_finance_fields(finance, data.get("crypto"))
            fields.extend(finance_fields)
        
        # Kalender
        calendar_fields = build_calendar_fields(self.settings.data_dir)
        fields.extend(calendar_fields)
        
        # Underholdning
        entertainment = build_entertainment_field(self.settings.data_dir)
        if entertainment:
            fields.append(entertainment)
        
        # Daglig utfordring
        challenge = self._get_daily_challenge()
        fields.append(challenge)
        
        # Legg til alle fields i embed
        for field in fields[:25]:  # Max 25 fields
            embed.fields.append(field)
        
        return DiscordMessage(embeds=[embed])

    def _get_daily_challenge(self) -> EmbedField:
        """Genererer daglig utfordring."""
        import random
        
        challenges = [
            "💪 Gjør 20 pushups før lunsj!",
            "🚶 Gå 10 000 skritt i dag",
            "📚 Les minst 20 sider i en bok",
            "🧘 Ta 10 minutter meditasjon",
            "💧 Drikk 8 glass vann i dag",
            "📵 1 time uten sosiale medier",
            "🍎 Spis 5 porsjoner frukt/grønt",
            "😊 Gi 3 komplimenter til andre",
            "📝 Skriv ned 3 ting du er takknemlig for",
            "🌳 Tilbring 30 min ute i naturen",
        ]
        
        return EmbedField(
            name="🎯 Dagens Utfordring",
            value=random.choice(challenges),
            inline=False,
        )
