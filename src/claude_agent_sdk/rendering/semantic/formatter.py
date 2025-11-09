"""UI element formatter for semantic role-based coloring.

This module implements ANSI formatting for UI messages using semantic
roles from Story 4.5. Follows research-validated patterns from Claude
Code CLI architecture analysis.

Based on findings:
- Combined ANSI sequences (\\033[31;1m) NOT separate (\\033[31m\\033[1m)
- Terminal capability detection via COLORTERM, TERM
- Graceful degradation for lower capability terminals
- Themeable color mappings

Usage:
    >>> from claude_agent_sdk.rendering.semantic import ANSIFormatter, default_theme
    >>> formatter = ANSIFormatter(theme=default_theme())
    >>> formatted = formatter.format("Error occurred", SemanticRole.ERROR)
    >>> print(formatted)  # "\\033[31;1mError occurred\\033[0m"
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .roles import SemanticRole
from .terminal_capability import TerminalCapability, get_capability
from .theme import ColorTheme, default_theme


@dataclass
class FormatterConfig:
    """Configuration for UI element formatting.

    Attributes:
        enable_color: Enable/disable color output globally
        theme: Color theme to use for formatting
        force_capability: Override terminal capability detection
        respect_no_color: Honor NO_COLOR environment variable
    """

    enable_color: bool = True
    theme: ColorTheme | None = None
    force_capability: TerminalCapability | None = None
    respect_no_color: bool = True

    def __post_init__(self):
        """Initialize default theme if not provided."""
        if self.theme is None:
            self.theme = default_theme()


class UIElementFormatter(ABC):
    """Abstract base class for UI element formatting.

    Subclasses implement the format() method to apply visual styling
    (colors, icons, formatting) to UI messages based on semantic roles.
    """

    @abstractmethod
    def format(self, content: str, role: SemanticRole) -> str:
        """Format content with styling for the given semantic role.

        Args:
            content: Text content to format
            role: Semantic role determining visual style

        Returns:
            str: Formatted content with ANSI escape sequences

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError


class ANSIFormatter(UIElementFormatter):
    """ANSI-based formatter for terminal output.

    Implements semantic role formatting using ANSI escape sequences.
    Follows Claude Code CLI patterns validated by research:
    - Combined escape sequences (e.g., \\033[31;1m)
    - Terminal capability detection
    - Graceful degradation
    - Themeable color mappings

    Usage:
        >>> formatter = ANSIFormatter()
        >>> error_msg = formatter.format("Failed", SemanticRole.ERROR)
        >>> print(error_msg)  # Displays in bright red
    """

    def __init__(self, config: FormatterConfig | None = None):
        """Initialize formatter with optional configuration.

        Args:
            config: Formatter configuration. Uses defaults if None.
        """
        self.config = config or FormatterConfig()
        self.capability = get_capability(force=self.config.force_capability)
        self._build_color_map()

    def _build_color_map(self) -> None:
        """Build ANSI color mapping from theme.

        Uses theme colors directly for COLOR_16 and higher.
        Degrades to monochrome if capability too low or color disabled.
        """
        if not self.config.enable_color or self.capability == TerminalCapability.MONOCHROME:
            # Monochrome mode - no colors
            self.color_map = dict.fromkeys(SemanticRole, "")
        else:
            # Use theme colors directly
            self.color_map = {role: self.config.theme.get_color(role) for role in SemanticRole}

    def format(self, content: str, role: SemanticRole) -> str:
        """Format content with ANSI colors based on semantic role.

        Applies ANSI escape sequences using combined format (e.g., \\033[31;1m)
        as validated by Claude Code Issue #6466 research.

        Args:
            content: Text content to format
            role: Semantic role determining color

        Returns:
            str: Content wrapped with ANSI escape sequences

        Example:
            >>> formatter = ANSIFormatter()
            >>> result = formatter.format("Error", SemanticRole.ERROR)
            >>> assert result == "\\033[31;1mError\\033[0m"
        """
        # Get color for role
        color_code = self.color_map.get(role, "")

        if not color_code:
            # No color - return plain content
            return content

        # Apply ANSI color with proper reset
        # Pattern: <color_code><content><reset>
        reset_code = "\033[0m"
        return f"{color_code}{content}{reset_code}"

    def format_with_icon(self, content: str, role: SemanticRole, icon: str | None = None) -> str:
        """Format content with optional icon prefix.

        Args:
            content: Text content to format
            role: Semantic role determining color
            icon: Optional icon to prepend (uses role.default_icon if None)

        Returns:
            str: Formatted content with icon prefix

        Example:
            >>> formatter = ANSIFormatter()
            >>> result = formatter.format_with_icon("Failed", SemanticRole.ERROR)
            >>> # Returns: "\\033[31;1m✗ Failed\\033[0m"
        """
        icon_str = icon if icon is not None else role.default_icon
        if icon_str:
            content = f"{icon_str} {content}"
        return self.format(content, role)

    def customize_theme(self, overrides: dict[SemanticRole, str]) -> "ANSIFormatter":
        """Create a new formatter with customized theme.

        Args:
            overrides: Color overrides for specific roles

        Returns:
            ANSIFormatter: New formatter with customized theme

        Example:
            >>> base = ANSIFormatter()
            >>> custom = base.customize_theme({
            ...     SemanticRole.ERROR: "\\033[91m",  # Different red
            ... })
        """
        new_theme = self.config.theme.customize(overrides)
        new_config = FormatterConfig(
            enable_color=self.config.enable_color,
            theme=new_theme,
            force_capability=self.config.force_capability,
            respect_no_color=self.config.respect_no_color,
        )
        return ANSIFormatter(config=new_config)
