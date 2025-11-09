"""Semantic formatter for structured data (JSON/YAML).

This module provides type-aware formatting for data formats where
coloring is based on value types rather than syntax tokens.

JSON Example:
    {
        "name": "value",     # key (dim), string value (green)
        "count": 42,         # key (dim), number value (green)
        "active": true       # key (dim), boolean (cyan)
    }

YAML Example:
    name: value              # key (blue), string value (red)
    count: 42                # key (blue), number value (green)
    active: true             # key (blue), boolean (cyan)

Usage:
    >>> formatter = StructuredDataFormatter(theme, semantic_mapping)
    >>> json_str = '{"status": "ok", "count": 42}'
    >>> formatted = formatter.format_json(json_str)
"""

import json
from typing import Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class StructuredDataFormatter:
    """Formats structured data with type-aware semantic coloring.

    Unlike syntax highlighting which colors based on syntax elements,
    this formatter colors based on data types (string, number, boolean, null).
    This matches Claude CLI's rendering of JSON/YAML in tool results.

    Supported Formats:
        - JSON: Semantic coloring for keys, values, and structure
        - YAML: Semantic coloring for keys, values, and comments

    Attributes:
        theme: Theme instance for styling
        semantic_mapping: Mapping from semantic categories to theme colors
    """

    def __init__(self, theme: 'Theme', semantic_mapping: 'SemanticMapping'):
        """Initialize formatter.

        Args:
            theme: Theme instance
            semantic_mapping: Semantic to theme category mapping
        """
        self.theme = theme
        self.semantic_mapping = semantic_mapping

    def format_json(self, data: str) -> str:
        """Format JSON with semantic type-based coloring.

        Color Mapping (from Story 1):
            - Keys: dim (metadata)
            - String values: green (success)
            - Number values: green (success)
            - Boolean values: cyan (info)
            - Null values: cyan (info)
            - Structure ({}, [], :, ,): white (assistant_message)

        Args:
            data: JSON string

        Returns:
            ANSI-styled JSON string

        Example:
            >>> formatter = StructuredDataFormatter(theme, mapping)
            >>> json_str = '{"name": "test", "count": 42, "active": true}'
            >>> print(formatter.format_json(json_str))
            # Output with colored: keys dim, "test" green, 42 green, true cyan
        """
        try:
            parsed = json.loads(data)
            return self._format_json_value(parsed, indent=0)
        except json.JSONDecodeError:
            # Not valid JSON - return as-is
            return data

    def _format_json_value(self, value: Any, indent: int) -> str:
        """Recursively format JSON value with type-aware coloring.

        Args:
            value: Python value (dict, list, str, int, float, bool, None)
            indent: Current indentation level

        Returns:
            Formatted string with ANSI color codes
        """
        indent_str = "  " * indent

        if isinstance(value, dict):
            if not value:
                return self._style("{}", "assistant_message")

            lines = [self._style("{", "assistant_message")]
            items = list(value.items())

            for i, (key, val) in enumerate(items):
                # Key (dim)
                key_styled = self._style(f'"{key}"', "metadata")
                # Colon (white)
                colon = self._style(": ", "assistant_message")
                # Value (recursive)
                val_formatted = self._format_json_value(val, indent + 1)
                # Comma (white)
                comma = self._style(",", "assistant_message") if i < len(items) - 1 else ""

                lines.append(f"{indent_str}  {key_styled}{colon}{val_formatted}{comma}")

            lines.append(indent_str + self._style("}", "assistant_message"))
            return "\n".join(lines)

        elif isinstance(value, list):
            if not value:
                return self._style("[]", "assistant_message")

            lines = [self._style("[", "assistant_message")]

            for i, item in enumerate(value):
                item_formatted = self._format_json_value(item, indent + 1)
                comma = self._style(",", "assistant_message") if i < len(value) - 1 else ""
                lines.append(f"{indent_str}  {item_formatted}{comma}")

            lines.append(indent_str + self._style("]", "assistant_message"))
            return "\n".join(lines)

        elif isinstance(value, str):
            # String values (green)
            return self._style(f'"{value}"', "success")

        elif isinstance(value, bool):
            # Boolean (cyan) - check bool before int!
            return self._style(str(value).lower(), "info")

        elif value is None:
            # Null (cyan)
            return self._style("null", "info")

        elif isinstance(value, int | float):
            # Numbers (green)
            return self._style(str(value), "success")

        else:
            # Unknown type - no styling
            return str(value)

    def format_yaml(self, data: str) -> str:
        """Format YAML with semantic coloring.

        Color Mapping (from Story 1):
            - Keys: blue (tool_use)
            - String values: red (error)
            - Number values: green (success)
            - Boolean/null values: cyan (info)
            - Comments: green (success)

        Args:
            data: YAML string

        Returns:
            ANSI-styled YAML string

        Note:
            Requires PyYAML. If not installed, returns original data.
        """
        if not YAML_AVAILABLE:
            return data

        try:
            # YAML formatting is line-based (simpler than JSON)
            lines = data.split('\n')
            formatted_lines = []

            for line in lines:
                formatted_lines.append(self._format_yaml_line(line))

            return '\n'.join(formatted_lines)

        except yaml.YAMLError:
            # Not valid YAML - return as-is
            return data

    def _format_yaml_line(self, line: str) -> str:
        """Format a single YAML line with semantic coloring.

        Args:
            line: YAML line

        Returns:
            Formatted line with ANSI codes
        """
        # Comment (green)
        if '#' in line:
            code_part, comment_part = line.split('#', 1)
            comment_styled = self._style(f"#{comment_part}", "success")
            if code_part.strip():
                code_styled = self._format_yaml_line(code_part.rstrip())
                return f"{code_styled}{comment_styled}"
            else:
                return f"{code_part}{comment_styled}"

        # Key-value pair
        if ':' in line and not line.strip().startswith('-'):
            key_part, value_part = line.split(':', 1)

            # Key (blue)
            key_styled = self._style(key_part, "tool_use")
            colon = self._style(":", "assistant_message")

            # Value (type-based)
            value = value_part.strip()
            if not value:
                return f"{key_styled}{colon}"
            elif value in ('true', 'false', 'True', 'False') or value in ('null', 'None', '~'):
                value_styled = self._style(value, "info")  # cyan
            elif value.replace('.', '').replace('-', '').isdigit():
                value_styled = self._style(value, "success")  # green (number)
            else:
                # String (red)
                value_styled = self._style(value, "error")

            # Preserve leading whitespace
            leading_space = value_part[:len(value_part) - len(value_part.lstrip())]
            return f"{key_styled}{colon}{leading_space}{value_styled}"

        # No formatting needed
        return line

    def _style(self, text: str, semantic_category: str) -> str:
        """Apply ANSI styling based on semantic category.

        Args:
            text: Text to style
            semantic_category: Semantic category (e.g., "success", "info")

        Returns:
            ANSI-styled text
        """
        from claude_agent_sdk.rendering.ansi import AnsiEncoder

        # Get theme category from semantic mapping
        theme_category = self.semantic_mapping.get_theme_category(semantic_category)

        # Get style rule from theme
        if hasattr(self.theme, theme_category):
            style_rule = getattr(self.theme, theme_category)
            encoder = AnsiEncoder()
            return encoder.encode(text, style_rule)

        # No styling
        return text

    def detect_format(self, text: str) -> str | None:
        """Detect if text is JSON or YAML.

        Args:
            text: Text to analyze

        Returns:
            "json", "yaml", or None

        Example:
            >>> formatter.detect_format('{"key": "value"}')
            'json'
            >>> formatter.detect_format('key: value')
            'yaml'
        """
        text = text.strip()

        # Try JSON first (most specific)
        if text.startswith(('{', '[')):
            try:
                json.loads(text)
                return "json"
            except json.JSONDecodeError:
                pass

        # Try YAML (more permissive)
        if YAML_AVAILABLE and (':' in text or text.startswith('-')):
            try:
                yaml.safe_load(text)
                return "yaml"
            except yaml.YAMLError:
                pass

        return None
