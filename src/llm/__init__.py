"""LLM integration layer for the Kali AI Command Chaining System."""

from .client import OllamaClient
from .prompts import PromptTemplates
from .context import ContextManager

__all__ = [
    "OllamaClient",
    "PromptTemplates",
    "ContextManager",
]