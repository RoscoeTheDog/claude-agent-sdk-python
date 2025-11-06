"""Pretty printer module for Claude SDK messages.

This module provides a pluggable rendering system for SDK messages,
matching the Claude Code CLI UTF-8 rendering format.

Public API:
    - MessageRenderer: Main rendering coordinator
    - RenderLevel: Message filtering levels
    - RendererConfig: Configuration for rendering
    - ClaudeCodeFormatter: UTF-8 formatter matching Claude CLI
    - StreamHandler: Console output handler
    - FileHandler: File output handler
    - NullHandler: No-op handler
    - display_message: Convenience function for quick usage
"""

from .base import Formatter, Handler, MessageRenderer
from .config import RendererConfig, RenderLevel

# Placeholder exports - will be populated as components are implemented
__all__ = [
    "Formatter",
    "Handler",
    "MessageRenderer",
    "RenderLevel",
    "RendererConfig",
    "ClaudeCodeFormatter",
    "StreamHandler",
    "FileHandler",
    "NullHandler",
    "display_message",
]
