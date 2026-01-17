"""
Datamodeller for Discord-meldinger.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class EmbedField(BaseModel):
    """Discord embed field."""
    
    name: str = Field(..., max_length=256)
    value: str = Field(..., max_length=1024)
    inline: bool = False

    @field_validator("value")
    @classmethod
    def truncate_value(cls, v: str) -> str:
        """Truncater verdi hvis for lang."""
        if len(v) > 1024:
            return v[:1021] + "..."
        return v


class EmbedFooter(BaseModel):
    """Discord embed footer."""
    
    text: str = Field(..., max_length=2048)
    icon_url: Optional[str] = None


class EmbedAuthor(BaseModel):
    """Discord embed author."""
    
    name: str = Field(..., max_length=256)
    url: Optional[str] = None
    icon_url: Optional[str] = None


class EmbedThumbnail(BaseModel):
    """Discord embed thumbnail."""
    
    url: str


class EmbedImage(BaseModel):
    """Discord embed image."""
    
    url: str


class Embed(BaseModel):
    """Discord embed."""
    
    title: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = Field(None, max_length=4096)
    url: Optional[str] = None
    color: Optional[int] = Field(None, ge=0, le=16777215)
    timestamp: Optional[datetime] = None
    footer: Optional[EmbedFooter] = None
    author: Optional[EmbedAuthor] = None
    thumbnail: Optional[EmbedThumbnail] = None
    image: Optional[EmbedImage] = None
    fields: list[EmbedField] = Field(default_factory=list, max_length=25)

    @field_validator("fields")
    @classmethod
    def validate_fields(cls, v: list[EmbedField]) -> list[EmbedField]:
        """Validerer antall fields."""
        if len(v) > 25:
            return v[:25]
        return v

    def add_field(
        self,
        name: str,
        value: str,
        inline: bool = False,
    ) -> "Embed":
        """Legger til et field."""
        if len(self.fields) < 25:
            self.fields.append(EmbedField(name=name, value=value, inline=inline))
        return self

    def to_dict(self) -> dict[str, Any]:
        """Konverterer til Discord API-format."""
        data = self.model_dump(exclude_none=True, mode="json")
        if self.timestamp:
            data["timestamp"] = self.timestamp.isoformat()
        return data


class DiscordMessage(BaseModel):
    """Discord webhook-melding."""
    
    content: Optional[str] = Field(None, max_length=2000)
    username: Optional[str] = Field(None, max_length=80)
    avatar_url: Optional[str] = None
    tts: bool = False
    embeds: list[Embed] = Field(default_factory=list, max_length=10)

    @field_validator("embeds")
    @classmethod
    def validate_embeds(cls, v: list[Embed]) -> list[Embed]:
        """Validerer antall embeds."""
        if len(v) > 10:
            return v[:10]
        return v

    def to_dict(self) -> dict[str, Any]:
        """Konverterer til Discord API-format."""
        data: dict[str, Any] = {}
        
        if self.content:
            data["content"] = self.content
        if self.username:
            data["username"] = self.username
        if self.avatar_url:
            data["avatar_url"] = self.avatar_url
        if self.tts:
            data["tts"] = self.tts
        if self.embeds:
            data["embeds"] = [embed.to_dict() for embed in self.embeds]
        
        return data

    @property
    def total_characters(self) -> int:
        """Totalt antall tegn i meldingen."""
        total = len(self.content or "")
        for embed in self.embeds:
            total += len(embed.title or "")
            total += len(embed.description or "")
            for field in embed.fields:
                total += len(field.name) + len(field.value)
        return total
