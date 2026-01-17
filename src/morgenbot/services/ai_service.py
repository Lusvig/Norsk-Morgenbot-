"""
Tjeneste for AI-generert innhold via Groq.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import structlog
from groq import AsyncGroq

from morgenbot.config.constants import WEEKDAYS
from morgenbot.services.base import BaseService

if TYPE_CHECKING:
    from morgenbot.config.settings import Settings


logger = structlog.get_logger(__name__)


class AIService(BaseService[str]):
    """
    Genererer AI-innhold via Groq API.
    """

    def __init__(self, settings: "Settings") -> None:
        super().__init__(settings)
        
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY er påkrevd for AIService")
        
        self.client = AsyncGroq(
            api_key=settings.groq_api_key.get_secret_value()
        )
        self.model = "llama-3.1-8b-instant"

    async def generate_greeting(self, data: dict[str, Any]) -> str | None:
        """
        Genererer personlig morgenmelding.
        
        Args:
            data: Samlet data fra andre tjenester
            
        Returns:
            AI-generert hilsning, eller None ved feil
        """
        try:
            prompt = self._build_greeting_prompt(data)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()

        except Exception as e:
            self.logger.error("ai_generation_failed", error=str(e))
            return None

    async def fetch(self) -> str | None:
        """Ikke implementert for AI-tjeneste."""
        return None

    def _build_greeting_prompt(self, data: dict[str, Any]) -> str:
        """Bygger prompt for hilsningsgenerering."""
        from datetime import datetime
        
        now = datetime.now()
        weekday = WEEKDAYS[now.weekday()]
        
        # Bygg kontekst fra data
        weather_info = ""
        if weather := data.get("weather"):
            temp = weather.current.temperature
            symbol = weather.current.condition.symbol_text
            weather_info = f"Vær: {temp}°C, {symbol}"
        
        news_info = ""
        if news := data.get("news"):
            top_titles = [n.title for n in news.top[:3]]
            news_info = f"Nyheter: {', '.join(top_titles)}"
        
        prompt = f"""Du er en hyggelig norsk morgenassistent. 
Lag en kort, personlig morgenmelding.

Dag: {weekday}
{weather_info}
{news_info}

Skriv 2-3 setninger. Vær varm og positiv. 
Tilpass til ukedagen. Ikke bruk emojis. Skriv på norsk."""

        return prompt
