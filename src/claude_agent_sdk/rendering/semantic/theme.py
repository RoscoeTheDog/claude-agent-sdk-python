"""Color theme definitions for semantic UI rendering.

This module defines color themes mapping semantic roles to ANSI color codes.
Based on research findings from Claude Code CLI color analysis.

Uses combined ANSI escape sequences (e.g., \\033[31;1m for bright red)
as validated by Claude Code Issue #6466 research.

Usage:
    >>> from claude_agent_sdk.rendering.semantic import ColorTheme, default_theme
    >>> theme = default_theme()
    >>> print(theme.colors[SemanticRole.ERROR])  # "\\033[31;1m"
"""

from dataclasses import dataclass, field

from .roles import SemanticRole


@dataclass
class ColorTheme:
    """Color theme for semantic UI rendering.

    Maps semantic roles to ANSI escape sequences. Supports customization
    via dict-based overrides.

    Attributes:
        name: Human-readable theme name
        colors: Mapping of SemanticRole -> ANSI escape sequence
        fallback_color: Color for unknown roles

    Example:
        >>> theme = ColorTheme(
        ...     name="Custom Theme",
        ...     colors={
        ...         SemanticRole.ERROR: "\\033[31;1m",  # Bright red
        ...         SemanticRole.SUCCESS: "\\033[32;1m",  # Bright green
        ...     }
        ... )
    """

    name: str
    colors: dict[SemanticRole, str] = field(default_factory=dict)
    fallback_color: str = "\033[0m"  # Default (no color)

    def customize(self, overrides: dict[SemanticRole, str]) -> "ColorTheme":
        """Create a customized copy of this theme.

        Args:
            overrides: Mapping of roles to override with new colors

        Returns:
            ColorTheme: New theme with overrides applied

        Example:
            >>> base = default_theme()
            >>> custom = base.customize({
            ...     SemanticRole.ERROR: "\\033[91m",  # Different red
            ... })
        """
        new_colors = {**self.colors, **overrides}
        return ColorTheme(
            name=f"{self.name} (customized)",
            colors=new_colors,
            fallback_color=self.fallback_color,
        )

    def get_color(self, role: SemanticRole) -> str:
        """Get ANSI color code for a semantic role.

        Args:
            role: Semantic role to get color for

        Returns:
            str: ANSI escape sequence

        Example:
            >>> theme = default_theme()
            >>> error_color = theme.get_color(SemanticRole.ERROR)
            >>> assert error_color == "\\033[31;1m"
        """
        return self.colors.get(role, self.fallback_color)


def default_theme() -> ColorTheme:
    """Create default color theme matching Claude Code CLI.

    Color mappings based on research findings:
    - System: Cyan (info)
    - User: Default (no color)
    - Assistant: Default (no color)
    - Tool: Magenta (tool activity)
    - Error: Bright red (bold)
    - Warning: Bright yellow (bold)
    - Success: Bright green (bold)
    - Info: Cyan
    - Code: Default (syntax highlighter handles)
    - Interactive: Blue (prompts, menus)

    ANSI codes use combined sequences (e.g., \\033[31;1m) as validated
    by Claude Code Issue #6466 research (NOT separate sequences).

    Returns:
        ColorTheme: Default theme matching Claude CLI

    Example:
        >>> theme = default_theme()
        >>> assert theme.name == "Claude Code Default"
    """
    return ColorTheme(
        name="Claude Code Default",
        colors={
            SemanticRole.SYSTEM: "\033[36m",  # Cyan (info)
            SemanticRole.USER: "\033[0m",  # Default (no color)
            SemanticRole.ASSISTANT: "\033[0m",  # Default (no color)
            SemanticRole.TOOL: "\033[35m",  # Magenta (tool activity)
            SemanticRole.ERROR: "\033[31;1m",  # Bright red (bold)
            SemanticRole.WARNING: "\033[33;1m",  # Bright yellow (bold)
            SemanticRole.SUCCESS: "\033[32;1m",  # Bright green (bold)
            SemanticRole.INFO: "\033[36m",  # Cyan
            SemanticRole.CODE: "\033[0m",  # Default (syntax handles)
            SemanticRole.INTERACTIVE: "\033[34m",  # Blue (prompts)
        },
        fallback_color="\033[0m",  # Default
    )


# Status indicator icons (from research findings)
STATUS_ICONS = {
    "running": "⟳",  # Unicode spinner
    "complete": "✓",  # Checkmark (green)
    "failed": "✗",  # Cross (red)
    "warning": "⚠️",  # Warning (yellow)
    "pending": "⊙",  # Circle (dim/grey)
}
