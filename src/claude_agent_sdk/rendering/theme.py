"""Theme system for terminal output styling.

This module provides a CSS-like theme system for styling terminal output with ANSI colors.
Themes consist of semantic style rules that map message types and UI elements to visual styles.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Any


class ColorDepth(IntEnum):
    """Terminal color capability levels.

    These levels represent the color support available in the terminal:
    - NONE: No color support (monochrome terminal)
    - BASIC_16: 16 basic ANSI colors (8 colors + 8 bright variants)
    - EXTENDED_256: 256-color palette (ANSI 256-color mode)
    - TRUECOLOR: 24-bit true color support (RGB)
    """

    NONE = 0
    BASIC_16 = 16
    EXTENDED_256 = 256
    TRUECOLOR = 16777216  # 2^24


@dataclass
class StyleRule:
    """Visual styling for a semantic category.

    This class defines the visual appearance of text in the terminal,
    similar to CSS rules. Colors can be specified as:
    - Named colors: "red", "bright_cyan", "blue"
    - RGB tuples: (255, 0, 0) for truecolor
    - 256-color indices: Integer 0-255

    Attributes:
        fg_color: Foreground (text) color
        bg_color: Background color
        bold: Enable bold/bright text
        dim: Enable dim/faint text
        italic: Enable italic text
        underline: Enable underlined text
    """

    fg_color: str | tuple[int, int, int] | int | None = None
    bg_color: str | tuple[int, int, int] | int | None = None
    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False


@dataclass
class Theme:
    """Collection of style rules for semantic categories.

    A Theme defines the visual appearance of all message types and UI elements
    in the terminal. Themes follow a CSS-like architecture where semantic
    categories (e.g., "error", "success") map to visual styles.

    Message Type Categories:
        user_message: User input messages
        assistant_message: Assistant responses
        system_message: System notifications

    Tool Categories:
        tool_use: Tool invocations
        tool_result: Successful tool results
        tool_error: Failed tool results

    Semantic Categories:
        error: Error messages
        warning: Warning messages
        success: Success messages
        info: Informational messages
        debug: Debug output

    UI Element Categories:
        bullet: List bullets (●)
        tree_connector: Tree structure connectors (⎿)
        metadata: Metadata like timestamps, cost
        truncation: Truncation indicators (...)

    Code Categories:
        code_block: Multi-line code blocks
        inline_code: Inline code snippets

    Special Categories:
        thinking: Assistant thinking/reasoning
        cost_display: Cost information display
    """

    # Message types
    user_message: StyleRule = field(default_factory=StyleRule)
    assistant_message: StyleRule = field(default_factory=StyleRule)
    system_message: StyleRule = field(default_factory=StyleRule)

    # Tool-related
    tool_use: StyleRule = field(default_factory=StyleRule)
    tool_result: StyleRule = field(default_factory=StyleRule)
    tool_error: StyleRule = field(default_factory=StyleRule)

    # Semantic categories
    error: StyleRule = field(default_factory=StyleRule)
    warning: StyleRule = field(default_factory=StyleRule)
    success: StyleRule = field(default_factory=StyleRule)
    info: StyleRule = field(default_factory=StyleRule)
    debug: StyleRule = field(default_factory=StyleRule)

    # UI elements
    bullet: StyleRule = field(default_factory=StyleRule)
    tree_connector: StyleRule = field(default_factory=StyleRule)
    metadata: StyleRule = field(default_factory=StyleRule)
    truncation: StyleRule = field(default_factory=StyleRule)

    # Code elements
    code_block: StyleRule = field(default_factory=StyleRule)
    inline_code: StyleRule = field(default_factory=StyleRule)

    # Special
    thinking: StyleRule = field(default_factory=StyleRule)
    cost_display: StyleRule = field(default_factory=StyleRule)

    @classmethod
    def claude_code_default(cls) -> Theme:
        """Create the default Claude Code CLI theme.

        This theme replicates the visual style of the official Claude Code CLI,
        providing a familiar experience for users transitioning to the SDK.

        Returns:
            Theme configured with Claude Code default colors
        """
        return cls(
            # Message types - neutral with subtle differentiation
            user_message=StyleRule(fg_color="bright_white", bold=True),
            assistant_message=StyleRule(fg_color="white"),
            system_message=StyleRule(fg_color="bright_black", dim=True),
            # Tool-related - blue family for tooling
            tool_use=StyleRule(fg_color="bright_blue", bold=True),
            tool_result=StyleRule(fg_color="blue"),
            tool_error=StyleRule(fg_color="bright_red", bold=True),
            # Semantic categories - standard color conventions
            error=StyleRule(fg_color="bright_red", bold=True),
            warning=StyleRule(fg_color="bright_yellow", bold=True),
            success=StyleRule(fg_color="bright_green", bold=True),
            info=StyleRule(fg_color="bright_cyan"),
            debug=StyleRule(fg_color="bright_black", dim=True),
            # UI elements - subtle, non-distracting
            bullet=StyleRule(fg_color="bright_black", dim=True),
            tree_connector=StyleRule(fg_color="bright_black", dim=True),
            metadata=StyleRule(fg_color="bright_black", dim=True),
            truncation=StyleRule(fg_color="bright_black", dim=True, italic=True),
            # Code elements - distinct but readable
            code_block=StyleRule(fg_color="cyan"),
            inline_code=StyleRule(fg_color="bright_cyan"),
            # Special
            thinking=StyleRule(fg_color="magenta", italic=True),
            cost_display=StyleRule(fg_color="bright_black", dim=True),
        )

    @classmethod
    def from_preset(cls, name: str) -> Theme:
        """Load a theme from a built-in preset.

        Args:
            name: Preset name (e.g., "claude_code", "solarized_dark")

        Returns:
            Theme instance for the specified preset

        Raises:
            ValueError: If preset name is not recognized
        """
        presets = {
            "claude_code": cls.claude_code_default,
            "claude_code_default": cls.claude_code_default,
        }

        preset_fn = presets.get(name.lower())
        if preset_fn is None:
            available = ", ".join(sorted(presets.keys()))
            raise ValueError(f"Unknown theme preset: {name!r}. Available: {available}")

        return preset_fn()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Theme:
        """Deserialize a theme from a dictionary.

        This method enables loading themes from JSON configuration files.
        The dictionary should map category names to style rule dictionaries.

        Args:
            data: Dictionary with category names as keys and style rule
                  dictionaries as values

        Returns:
            Theme instance deserialized from the dictionary

        Example:
            >>> data = {
            ...     "error": {"fg_color": "red", "bold": True},
            ...     "success": {"fg_color": "green"}
            ... }
            >>> theme = Theme.from_dict(data)
        """
        # Convert nested dicts to StyleRule objects
        kwargs = {}
        for key, value in data.items():
            if isinstance(value, dict):
                kwargs[key] = StyleRule(**value)
            elif isinstance(value, StyleRule):
                kwargs[key] = value
            else:
                raise ValueError(
                    f"Invalid value for theme category {key!r}: "
                    f"expected dict or StyleRule, got {type(value).__name__}"
                )

        return cls(**kwargs)

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """Serialize the theme to a dictionary.

        This method enables saving themes to JSON configuration files.
        All StyleRule objects are converted to dictionaries.

        Returns:
            Dictionary representation suitable for JSON serialization

        Example:
            >>> theme = Theme.claude_code_default()
            >>> data = theme.to_dict()
            >>> data["error"]
            {'fg_color': 'bright_red', 'bg_color': None, 'bold': True, ...}
        """
        result = {}
        for key, value in asdict(self).items():
            if isinstance(value, dict):
                result[key] = value
            else:
                # Should not happen with dataclass asdict(), but handle gracefully
                result[key] = asdict(value) if hasattr(value, "__dict__") else value
        return result
