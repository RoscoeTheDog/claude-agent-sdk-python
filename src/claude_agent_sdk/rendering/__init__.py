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
    - Theme: Theme configuration with semantic style categories
    - StyleRule: Style definition for a semantic category
    - ColorDepth: Terminal color capability levels
"""

from typing import TextIO

from ..types import Message
from .base import Formatter, Handler, MessageRenderer
from .config import RendererConfig, RenderLevel, SystemMessageLevel
from .formatters import ClaudeCodeFormatter
from .handlers import FileHandler, NullHandler, StreamHandler
from .theme import ColorDepth, StyleRule, Theme

# Singleton renderer for convenience function
_default_renderer: MessageRenderer | None = None


def display_message(
    message: Message,
    level: RenderLevel = RenderLevel.STANDARD,
    stream: TextIO | None = None,
) -> None:
    """Display a message using a singleton renderer with default configuration.

    This is a convenience function for quick usage without setting up a full
    renderer. It uses a singleton MessageRenderer with ClaudeCodeFormatter
    and StreamHandler.

    Args:
        message: The Message object to render
        level: The render level to use (default: STANDARD)
        stream: The output stream (default: stdout)

    Example:
        >>> from claude_agent_sdk.rendering import display_message, RenderLevel
        >>> display_message(message)
        >>> display_message(message, level=RenderLevel.DETAILED)
    """
    global _default_renderer
    import sys

    if _default_renderer is None:
        # Initialize singleton renderer
        config = RendererConfig(render_level=level)
        formatter = ClaudeCodeFormatter(config)
        handler = StreamHandler(stream=stream or sys.stdout, formatter=formatter)
        _default_renderer = MessageRenderer()
        _default_renderer.add_handler(handler)

    _default_renderer.render(message)


__all__ = [
    "Formatter",
    "Handler",
    "MessageRenderer",
    "RenderLevel",
    "SystemMessageLevel",
    "RendererConfig",
    "ClaudeCodeFormatter",
    "StreamHandler",
    "FileHandler",
    "NullHandler",
    "display_message",
    "Theme",
    "StyleRule",
    "ColorDepth",
]
