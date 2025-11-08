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
    def solarized_dark(cls) -> Theme:
        """Create a Solarized Dark theme.

        Based on the popular Solarized color scheme by Ethan Schoonover.
        Designed for low-contrast, easy-on-the-eyes terminal usage.

        Official palette:
        - base03: #002b36 (background)
        - base0: #839496 (body text)
        - yellow: #b58900
        - orange: #cb4b16
        - red: #dc322f
        - magenta: #d33682
        - violet: #6c71c4
        - blue: #268bd2
        - cyan: #2aa198
        - green: #859900

        Returns:
            Theme configured with Solarized Dark colors
        """
        # Solarized palette (256-color approximations)
        base0 = 244  # #839496 (body text)
        base01 = 240  # #586e75 (emphasized text)
        yellow = 136  # #b58900
        red = 160  # #dc322f
        magenta = 168  # #d33682
        blue = 32  # #268bd2
        cyan = 37  # #2aa198
        green = 100  # #859900

        return cls(
            # Message types
            user_message=StyleRule(fg_color=base0, bold=True),
            assistant_message=StyleRule(fg_color=base0),
            system_message=StyleRule(fg_color=base01, dim=True),
            # Tool-related
            tool_use=StyleRule(fg_color=blue, bold=True),
            tool_result=StyleRule(fg_color=cyan),
            tool_error=StyleRule(fg_color=red, bold=True),
            # Semantic categories
            error=StyleRule(fg_color=red, bold=True),
            warning=StyleRule(fg_color=yellow, bold=True),
            success=StyleRule(fg_color=green, bold=True),
            info=StyleRule(fg_color=cyan),
            debug=StyleRule(fg_color=base01, dim=True),
            # UI elements
            bullet=StyleRule(fg_color=base01),
            tree_connector=StyleRule(fg_color=base01),
            metadata=StyleRule(fg_color=base01, dim=True),
            truncation=StyleRule(fg_color=base01, dim=True, italic=True),
            # Code elements
            code_block=StyleRule(fg_color=cyan),
            inline_code=StyleRule(fg_color=blue),
            # Special
            thinking=StyleRule(fg_color=magenta, italic=True),
            cost_display=StyleRule(fg_color=base01, dim=True),
        )

    @classmethod
    def solarized_light(cls) -> Theme:
        """Create a Solarized Light theme.

        Light variant of the Solarized color scheme.
        Same colors as Solarized Dark but inverted background/foreground.

        Official palette (same colors, different base):
        - base3: #fdf6e3 (background)
        - base00: #657b83 (body text)
        - Other colors remain the same

        Returns:
            Theme configured with Solarized Light colors
        """
        # Solarized palette (256-color approximations)
        base00 = 241  # #657b83 (body text)
        base01 = 240  # #586e75 (emphasized text)
        yellow = 136  # #b58900
        red = 160  # #dc322f
        magenta = 168  # #d33682
        blue = 32  # #268bd2
        cyan = 37  # #2aa198
        green = 100  # #859900

        return cls(
            # Message types
            user_message=StyleRule(fg_color=base00, bold=True),
            assistant_message=StyleRule(fg_color=base00),
            system_message=StyleRule(fg_color=base01),
            # Tool-related
            tool_use=StyleRule(fg_color=blue, bold=True),
            tool_result=StyleRule(fg_color=cyan),
            tool_error=StyleRule(fg_color=red, bold=True),
            # Semantic categories
            error=StyleRule(fg_color=red, bold=True),
            warning=StyleRule(fg_color=yellow, bold=True),
            success=StyleRule(fg_color=green, bold=True),
            info=StyleRule(fg_color=cyan),
            debug=StyleRule(fg_color=base01),
            # UI elements
            bullet=StyleRule(fg_color=base01),
            tree_connector=StyleRule(fg_color=base01),
            metadata=StyleRule(fg_color=base01),
            truncation=StyleRule(fg_color=base01, italic=True),
            # Code elements
            code_block=StyleRule(fg_color=cyan),
            inline_code=StyleRule(fg_color=blue),
            # Special
            thinking=StyleRule(fg_color=magenta, italic=True),
            cost_display=StyleRule(fg_color=base01),
        )

    @classmethod
    def gruvbox(cls) -> Theme:
        """Create a Gruvbox theme.

        Based on the Gruvbox color scheme by Pavel Pertsev.
        Warm, retro-inspired colors with medium contrast.

        Official palette (dark variant):
        - bg0: #282828 (background)
        - fg1: #ebdbb2 (foreground)
        - red: #cc241d
        - green: #98971a
        - yellow: #d79921
        - blue: #458588
        - purple: #b16286
        - aqua: #689d6a
        - orange: #d65d0e

        Returns:
            Theme configured with Gruvbox colors
        """
        # Gruvbox palette (256-color approximations)
        fg1 = 223  # #ebdbb2 (foreground)
        gray = 245  # #928374 (gray)
        red = 167  # #fb4934 (bright red)
        green = 142  # #b8bb26 (bright green)
        yellow = 214  # #fabd2f (bright yellow)
        blue = 109  # #83a598 (bright blue)
        purple = 175  # #d3869b (bright purple)
        aqua = 108  # #8ec07c (bright aqua)
        aqua_dim = 72  # #689d6a (aqua)

        return cls(
            # Message types
            user_message=StyleRule(fg_color=fg1, bold=True),
            assistant_message=StyleRule(fg_color=fg1),
            system_message=StyleRule(fg_color=gray, dim=True),
            # Tool-related
            tool_use=StyleRule(fg_color=blue, bold=True),
            tool_result=StyleRule(fg_color=aqua),
            tool_error=StyleRule(fg_color=red, bold=True),
            # Semantic categories
            error=StyleRule(fg_color=red, bold=True),
            warning=StyleRule(fg_color=yellow, bold=True),
            success=StyleRule(fg_color=green, bold=True),
            info=StyleRule(fg_color=aqua),
            debug=StyleRule(fg_color=gray, dim=True),
            # UI elements
            bullet=StyleRule(fg_color=gray),
            tree_connector=StyleRule(fg_color=gray),
            metadata=StyleRule(fg_color=gray, dim=True),
            truncation=StyleRule(fg_color=gray, dim=True, italic=True),
            # Code elements
            code_block=StyleRule(fg_color=aqua_dim),
            inline_code=StyleRule(fg_color=blue),
            # Special
            thinking=StyleRule(fg_color=purple, italic=True),
            cost_display=StyleRule(fg_color=gray, dim=True),
        )

    @classmethod
    def nord(cls) -> Theme:
        """Create a Nord theme.

        Based on the Nord color scheme by Arctic Ice Studio.
        Cool, arctic-inspired blue/cyan palette with good contrast.

        Official palette:
        - nord0: #2e3440 (background)
        - nord4: #d8dee9 (foreground)
        - nord11: #bf616a (red)
        - nord13: #ebcb8b (yellow)
        - nord14: #a3be8c (green)
        - nord9: #81a1c1 (blue)
        - nord15: #b48ead (purple)
        - nord8: #88c0d0 (cyan)
        - nord12: #d08770 (orange)

        Returns:
            Theme configured with Nord colors
        """
        # Nord palette (256-color approximations)
        nord3 = 246  # #4c566a (bright black)
        nord4 = 252  # #d8dee9 (foreground)
        nord6 = 254  # #eceff4 (bright foreground)
        nord8 = 116  # #88c0d0 (cyan)
        nord9 = 110  # #81a1c1 (blue)
        nord11 = 167  # #bf616a (red)
        nord13 = 222  # #ebcb8b (yellow)
        nord14 = 150  # #a3be8c (green)
        nord15 = 182  # #b48ead (purple)

        return cls(
            # Message types
            user_message=StyleRule(fg_color=nord6, bold=True),
            assistant_message=StyleRule(fg_color=nord4),
            system_message=StyleRule(fg_color=nord3, dim=True),
            # Tool-related
            tool_use=StyleRule(fg_color=nord9, bold=True),
            tool_result=StyleRule(fg_color=nord8),
            tool_error=StyleRule(fg_color=nord11, bold=True),
            # Semantic categories
            error=StyleRule(fg_color=nord11, bold=True),
            warning=StyleRule(fg_color=nord13, bold=True),
            success=StyleRule(fg_color=nord14, bold=True),
            info=StyleRule(fg_color=nord8),
            debug=StyleRule(fg_color=nord3, dim=True),
            # UI elements
            bullet=StyleRule(fg_color=nord3),
            tree_connector=StyleRule(fg_color=nord3),
            metadata=StyleRule(fg_color=nord3, dim=True),
            truncation=StyleRule(fg_color=nord3, dim=True, italic=True),
            # Code elements
            code_block=StyleRule(fg_color=nord8),
            inline_code=StyleRule(fg_color=nord9),
            # Special
            thinking=StyleRule(fg_color=nord15, italic=True),
            cost_display=StyleRule(fg_color=nord3, dim=True),
        )

    @classmethod
    def monochrome(cls) -> Theme:
        """Create a monochrome theme.

        No colors, only bold/dim for emphasis.
        Ideal for black-and-white terminals or screenshot documentation.

        Returns:
            Theme configured with no colors, only font styles
        """
        return cls(
            # Message types - differentiate with bold
            user_message=StyleRule(bold=True),
            assistant_message=StyleRule(),
            system_message=StyleRule(dim=True),
            # Tool-related - bold for actions
            tool_use=StyleRule(bold=True),
            tool_result=StyleRule(),
            tool_error=StyleRule(bold=True, underline=True),
            # Semantic categories - use bold/underline
            error=StyleRule(bold=True, underline=True),
            warning=StyleRule(bold=True),
            success=StyleRule(bold=True),
            info=StyleRule(),
            debug=StyleRule(dim=True),
            # UI elements - subtle
            bullet=StyleRule(dim=True),
            tree_connector=StyleRule(dim=True),
            metadata=StyleRule(dim=True),
            truncation=StyleRule(dim=True, italic=True),
            # Code elements - italic for code
            code_block=StyleRule(italic=True),
            inline_code=StyleRule(italic=True),
            # Special
            thinking=StyleRule(italic=True),
            cost_display=StyleRule(dim=True),
        )

    @classmethod
    def high_contrast(cls) -> Theme:
        """Create a high-contrast theme.

        Maximum contrast for accessibility.
        Uses bright colors on dark background with bold emphasis.

        Designed for:
        - Users with visual impairments
        - High ambient light conditions
        - Presentation/demo scenarios

        Returns:
            Theme configured for maximum contrast
        """
        return cls(
            # Message types - bright and bold
            user_message=StyleRule(fg_color="bright_white", bold=True),
            assistant_message=StyleRule(fg_color="bright_white"),
            system_message=StyleRule(fg_color="white"),
            # Tool-related - bright blue for contrast
            tool_use=StyleRule(fg_color="bright_blue", bold=True),
            tool_result=StyleRule(fg_color="bright_cyan", bold=True),
            tool_error=StyleRule(fg_color="bright_red", bold=True, underline=True),
            # Semantic categories - maximum saturation
            error=StyleRule(fg_color="bright_red", bold=True, underline=True),
            warning=StyleRule(fg_color="bright_yellow", bold=True, underline=True),
            success=StyleRule(fg_color="bright_green", bold=True, underline=True),
            info=StyleRule(fg_color="bright_cyan", bold=True),
            debug=StyleRule(fg_color="white"),
            # UI elements - visible but not distracting
            bullet=StyleRule(fg_color="white", bold=True),
            tree_connector=StyleRule(fg_color="white", bold=True),
            metadata=StyleRule(fg_color="white"),
            truncation=StyleRule(fg_color="white", italic=True),
            # Code elements - bright and distinguishable
            code_block=StyleRule(fg_color="bright_cyan"),
            inline_code=StyleRule(fg_color="bright_blue", bold=True),
            # Special
            thinking=StyleRule(fg_color="bright_magenta", bold=True, italic=True),
            cost_display=StyleRule(fg_color="white"),
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
            "solarized_dark": cls.solarized_dark,
            "solarized_light": cls.solarized_light,
            "gruvbox": cls.gruvbox,
            "nord": cls.nord,
            "monochrome": cls.monochrome,
            "high_contrast": cls.high_contrast,
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
