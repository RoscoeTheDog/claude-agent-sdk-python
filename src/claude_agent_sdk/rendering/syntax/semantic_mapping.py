"""Semantic category to theme color mapping.

This module provides the customization layer between semantic categories
(from TokenMapper) and theme colors. Users can create custom mappings
to achieve different syntax coloring schemes.

Usage:
    >>> # Use default Claude CLI mapping
    >>> mapping = SemanticMapping.claude_default()
    >>> mapping.get_theme_category("keyword")
    'tool_use'  # Maps to blue
    >>>
    >>> # Customize for specific language
    >>> custom = mapping.customize({
    ...     "comment": "metadata",  # Dim instead of green
    ...     "string_literal": "success"  # Green instead of red
    ... })
"""

from dataclasses import dataclass, field


@dataclass
class SemanticMapping:
    """Maps semantic categories to theme category names.

    This is the customization layer where users can override how
    syntax elements map to theme colors. For example, you could
    make all comments dim instead of green, or make strings cyan
    instead of red.

    The mapping is extensible - new semantic categories can be added
    without breaking existing themes (they'll use the default fallback).

    Attributes:
        mappings: Dict mapping semantic category name to theme category name

    Example:
        >>> mapping = SemanticMapping()
        >>> mapping.get_theme_category("keyword")
        'tool_use'  # Keywords map to blue (tool_use style)
    """

    mappings: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize with Claude CLI default mappings if empty."""
        if not self.mappings:
            self.mappings = self._get_claude_defaults()

    @staticmethod
    def _get_claude_defaults() -> dict[str, str]:
        """Get default mappings matching Claude CLI (from Story 1).

        Returns:
            Dict mapping semantic categories to theme categories
        """
        return {
            # Keywords & Control Flow
            "keyword": "tool_use",              # blue
            "keyword_operator": "tool_use",     # blue (and, or, not)

            # Literals
            "string_literal": "error",          # red
            "escape_sequence": "error",         # red
            "number_literal": "success",        # green
            "boolean_literal": "info",          # cyan

            # Comments & Documentation
            "comment": "success",               # green
            "doc_string": "success",            # green

            # Types & Classes
            "type_annotation": "info",          # cyan
            "class_type": "info",               # cyan (in type hints)
            "class_name": "assistant_message",  # white (in definition)

            # Functions & Identifiers
            "builtin_function": "tool_use",     # blue
            "function_name": "assistant_message",  # white
            "decorator": "assistant_message",      # white
            "identifier": "assistant_message",     # white

            # Special Identifiers
            "special_identifier": "info",       # cyan (self, this, cls)

            # Operators & Punctuation
            "operator": "assistant_message",    # white
            "punctuation": "assistant_message", # white

            # Whitespace
            "whitespace": "assistant_message",  # no styling

            # Fallbacks
            "default": "assistant_message",     # white
            "error": "error",                   # red (for syntax errors)
            "success": "success",               # green (for diffs)
        }

    @classmethod
    def claude_default(cls) -> 'SemanticMapping':
        """Create mapping with Claude CLI defaults.

        Returns:
            SemanticMapping configured to match Claude CLI rendering
        """
        return cls(mappings=cls._get_claude_defaults())

    def get_theme_category(self, semantic_category: str) -> str:
        """Get theme category name for a semantic category.

        Args:
            semantic_category: Semantic category from TokenMapper
                             (e.g., "keyword", "string_literal")

        Returns:
            Theme category name (e.g., "tool_use", "error")

        Example:
            >>> mapping = SemanticMapping()
            >>> mapping.get_theme_category("keyword")
            'tool_use'
            >>> mapping.get_theme_category("string_literal")
            'error'
        """
        return self.mappings.get(semantic_category, self.mappings.get("default", "assistant_message"))

    def customize(self, overrides: dict[str, str]) -> 'SemanticMapping':
        """Create customized mapping with overrides.

        Args:
            overrides: Dict mapping semantic categories to new theme categories

        Returns:
            New SemanticMapping with overrides applied

        Example:
            >>> base = SemanticMapping.claude_default()
            >>> custom = base.customize({
            ...     "comment": "metadata",     # Dim comments
            ...     "string_literal": "success"  # Green strings
            ... })
        """
        new_mappings = self.mappings.copy()
        new_mappings.update(overrides)
        return SemanticMapping(mappings=new_mappings)

    def validate(self, theme: 'Theme') -> list[str]:
        """Validate that all theme categories exist in theme.

        Args:
            theme: Theme to validate against

        Returns:
            List of invalid theme category names (empty if all valid)

        Example:
            >>> mapping = SemanticMapping()
            >>> theme = Theme.claude_code_default()
            >>> errors = mapping.validate(theme)
            >>> if errors:
            ...     print(f"Invalid categories: {errors}")
        """
        invalid = []
        for semantic_cat, theme_cat in self.mappings.items():
            if not hasattr(theme, theme_cat):
                invalid.append(f"{semantic_cat} -> {theme_cat}")
        return invalid
