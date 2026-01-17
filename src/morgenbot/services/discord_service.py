"""
Tjeneste for Discord-kommunikasjon.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import structlog

from morgenbot.exceptions.errors import DiscordError
from morgenbot.models.discord import DiscordMessage

if TYPE_CHECKING:
    from morgenbot.config.settings import Settings


logger = structlog.get_logger(__name__)


class DiscordService:
    """
    Sender meldinger til Discord via webhook.
    """

    def __init__(self, settings: "Settings") -> None:
        self.webhook_url = str(settings.discord_webhook)
        self.timeout = settings.request_timeout
        self.logger = logger.bind(service="DiscordService")

    async def send(self, message: DiscordMessage) -> bool:
        """
        Sender melding til Discord.
        
        Args:
            message: Melding å sende
            
        Returns:
            True hvis meldingen ble sendt
            
        Raises:
            DiscordError: Hvis sending feiler
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url,
                    json=message.to_dict(),
                    headers={"Content-Type": "application/json"},
                )
                
                if response.status_code == 204:
                    self.logger.info("message_sent")
                    return True
                
                self.logger.error(
                    "discord_error",
                    status_code=response.status_code,
                    response=response.text,
                )
                raise DiscordError(f"Discord returnerte {response.status_code}")

        except httpx.HTTPError as e:
            self.logger.error("discord_http_error", error=str(e))
            raise DiscordError(f"HTTP-feil: {e}") from e

    async def send_error_notification(self, error: Exception) -> None:
        """Sender feilmelding til Discord."""
        from morgenbot.models.discord import Embed
        
        message = DiscordMessage(
            embeds=[
                Embed(
                    title="⚠️ Morgenbot Feil",
                    description=f"```\n{error}\n```",
                    color=0xE74C3C,
                )
            ]
        )
        
        try:
            await self.send(message)
        except DiscordError:
            self.logger.exception("failed_to_send_error_notification")
