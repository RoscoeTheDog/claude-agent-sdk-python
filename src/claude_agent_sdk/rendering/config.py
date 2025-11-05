"""Configuration classes for the rendering system.

This module provides configuration classes and enums for controlling
message rendering behavior.
"""

from dataclasses import dataclass, field
from enum import IntEnum


class RenderLevel(IntEnum):
    """Message filtering levels for controlling rendering detail.

    Levels are ordered from least to most detailed:
    - MINIMAL: Only user and assistant text
    - STANDARD: + tool names and summaries (default)
    - DETAILED: + tool inputs and outputs
    - DEBUG: + system messages
    - ALL: Everything including stream events
    """

    MINIMAL = 0
    STANDARD = 1
    DETAILED = 2
    DEBUG = 3
    ALL = 4


@dataclass
class RendererConfig:
    """Configuration for message rendering.

    This class controls all aspects of message rendering including
    filtering, formatting, and display options.
    """

    # Filtering
    render_level: RenderLevel = RenderLevel.STANDARD
    include_message_types: list[str] = field(default_factory=list)
    exclude_message_types: list[str] = field(default_factory=list)

    # Display settings
    show_metadata: bool = False
    show_tool_inputs: bool = True
    show_tool_outputs: bool = True
    compact_mode: bool = False

    # Content limits
    max_text_length: int = 10000
    max_tool_output_length: int = 5000

    # UTF-8 characters (matching Claude Code CLI)
    bullet: str = "\u25cf"  # ●
    tree_connector: str = "\u23bf"  # ⎿
    arrow: str = "\u2192"  # →
    ellipsis: str = "\u2026"  # …
    list_bullet: str = "\u00b7"  # ·

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.max_text_length < 0:
            raise ValueError("max_text_length must be non-negative")
        if self.max_tool_output_length < 0:
            raise ValueError("max_tool_output_length must be non-negative")
