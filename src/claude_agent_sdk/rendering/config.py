"""Configuration classes for the rendering system.

This module provides configuration classes and enums for controlling
message rendering behavior.
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Any

from .ansi import detect_color_depth
from .theme import ColorDepth, Theme


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
    filtering, formatting, display options, and color/theme settings.
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
    show_cost: bool = False  # Hide cost by default (matches Claude CLI)

    # Content limits
    max_text_length: int = 10000
    max_tool_output_length: int = 5000

    # UTF-8 characters (matching Claude Code CLI)
    bullet: str = "\u25cf"  # ●
    tree_connector: str = "\u23bf"  # ⎿
    arrow: str = "\u2192"  # →
    ellipsis: str = "\u2026"  # …
    list_bullet: str = "\u00b7"  # ·

    # Color and theme settings (Sprint 1.3)
    theme: Theme = field(default_factory=Theme.claude_code_default)
    color_enabled: bool = True
    color_depth: ColorDepth | None = None  # Auto-detect if None
    screen_reader_mode: bool = False  # For future use

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.max_text_length < 0:
            raise ValueError("max_text_length must be non-negative")
        if self.max_tool_output_length < 0:
            raise ValueError("max_tool_output_length must be non-negative")

        # Auto-detect color depth if not specified
        if self.color_depth is None and self.color_enabled:
            self.color_depth = _detect_color_depth()

        # Disable color if not a TTY
        if self.color_enabled and not _is_tty():
            self.color_enabled = False
            self.color_depth = ColorDepth.NONE

    @classmethod
    def from_file(cls, path: str | Path) -> "RendererConfig":
        """Load configuration from a JSON file.

        Args:
            path: Path to the JSON configuration file

        Returns:
            RendererConfig instance loaded from the file

        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file is not valid JSON
            ValueError: If the config contains invalid values
        """
        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return cls._from_dict(data)

    @classmethod
    def load_defaults(cls) -> "RendererConfig":
        """Load configuration with cascading priority.

        Config priority (highest to lowest):
        1. Project-level: ./.claude-sdk/config.json
        2. User-level: ~/.claude-sdk/config.json
        3. Built-in defaults

        Returns:
            RendererConfig with merged settings from all sources
        """
        # Start with built-in defaults
        config_dict: dict[str, Any] = {}

        # Try user-level config
        user_config_path = Path.home() / ".claude-sdk" / "config.json"
        if user_config_path.exists():
            with user_config_path.open("r", encoding="utf-8") as f:
                user_config = json.load(f)
                config_dict = _merge_configs(config_dict, user_config)

        # Try project-level config
        project_config_path = Path.cwd() / ".claude-sdk" / "config.json"
        if project_config_path.exists():
            with project_config_path.open("r", encoding="utf-8") as f:
                project_config = json.load(f)
                config_dict = _merge_configs(config_dict, project_config)

        # Create config from merged dict, or use defaults if no configs found
        if config_dict:
            return cls._from_dict(config_dict)
        else:
            return cls()

    def to_file(self, path: str | Path) -> None:
        """Save configuration to a JSON file.

        Args:
            path: Path where the configuration should be saved

        Note:
            Creates parent directories if they don't exist.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = self._to_dict()
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> "RendererConfig":
        """Create a RendererConfig from a dictionary.

        Args:
            data: Dictionary containing configuration values

        Returns:
            RendererConfig instance
        """
        # Handle theme deserialization
        if "theme" in data:
            if isinstance(data["theme"], str):
                # Preset name
                data["theme"] = Theme.from_preset(data["theme"])
            elif isinstance(data["theme"], dict):
                # Custom theme dict
                data["theme"] = Theme.from_dict(data["theme"])

        # Handle color_depth deserialization
        if "color_depth" in data and data["color_depth"] is not None:
            if isinstance(data["color_depth"], str):
                data["color_depth"] = ColorDepth[data["color_depth"]]
            elif isinstance(data["color_depth"], int):
                data["color_depth"] = ColorDepth(data["color_depth"])

        # Handle render_level deserialization
        if "render_level" in data:
            if isinstance(data["render_level"], str):
                data["render_level"] = RenderLevel[data["render_level"]]
            elif isinstance(data["render_level"], int):
                data["render_level"] = RenderLevel(data["render_level"])

        return cls(**data)

    def _to_dict(self) -> dict[str, Any]:
        """Convert config to a dictionary for serialization.

        Returns:
            Dictionary representation of the configuration
        """
        data = asdict(self)

        # Convert theme to dict
        if "theme" in data and isinstance(self.theme, Theme):
            data["theme"] = self.theme.to_dict()

        # Convert color_depth to string name (or null)
        if "color_depth" in data and self.color_depth is not None:
            data["color_depth"] = self.color_depth.name

        # Convert render_level to string name
        if "render_level" in data:
            data["render_level"] = self.render_level.name

        return data


def _detect_color_depth() -> ColorDepth:
    """Detect terminal color capabilities.

    Returns:
        ColorDepth enum indicating the terminal's color support
    """
    return detect_color_depth()


def _is_tty() -> bool:
    """Check if stdout is a TTY.

    Returns:
        True if stdout is a terminal, False otherwise
    """
    return sys.stdout.isatty()


def _merge_configs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge two configuration dictionaries.

    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary (takes precedence)

    Returns:
        Merged configuration dictionary
    """
    merged = base.copy()
    merged.update(override)
    return merged
