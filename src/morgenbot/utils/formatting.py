"""
Formatteringsfunksjoner for Discord.
"""

from __future__ import annotations


def bold(text: str) -> str:
    """
    Formaterer tekst som bold i Discord.
    
    Args:
        text: Tekst å formatere
        
    Returns:
        Formatert tekst
    """
    return f"**{text}**"


def italic(text: str) -> str:
    """
    Formaterer tekst som italic i Discord.
    
    Args:
        text: Tekst å formatere
        
    Returns:
        Formatert tekst
    """
    return f"*{text}*"


def inline_code(text: str) -> str:
    """
    Formaterer tekst som inline code i Discord.
    
    Args:
        text: Tekst å formatere
        
    Returns:
        Formatert tekst
    """
    return f"`{text}`"


def code_block(text: str, language: str = "") -> str:
    """
    Formaterer tekst som code block i Discord.
    
    Args:
        text: Tekst å formatere
        language: Språk for syntax highlighting
        
    Returns:
        Formatert tekst
    """
    return f"```{language}\n{text}\n```"
