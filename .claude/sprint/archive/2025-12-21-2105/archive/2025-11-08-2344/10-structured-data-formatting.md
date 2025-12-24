# Story 10: Structured Data Formatting

**Status**: unassigned
**Assignee**: unassigned
**Estimated Time**: 2 hours
**Actual Time**: TBD
**Priority**: HIGH

---

## Dependencies

- Story 1 (COMPLETED) - Provides structured data color mappings
- Story 2 (unassigned) - Theme foundation
- Reference: `.claude/implementation/stories/1-color-analysis.md` - Section: "Structured Data (JSON Output)"

---

## Description

Implement semantic coloring for structured data (JSON/YAML) in tool results to match Claude CLI's visual presentation. JSON keys, string values, numbers, booleans, and null values each receive distinct styling based on their semantic type.

**Critical Finding**: Claude CLI applies **semantic type-based coloring** to JSON/YAML, not simple syntax highlighting. This requires parsing and type detection, not just Pygments.

**Goal**: Match Claude CLI's structured data presentation exactly.

---

## Acceptance Criteria

### JSON Formatting
- [ ] Property names (keys) → `bright_black` (dim)
- [ ] String values → `green`
- [ ] Number values → `green`
- [ ] Boolean values (`true`, `false`) → `cyan`
- [ ] Null values (`null`) → `cyan`
- [ ] Structural characters (`{`, `}`, `[`, `]`, `:`, `,`) → `white`

### YAML Formatting
- [ ] Keys → `blue`
- [ ] String values → `red`
- [ ] Number values → `green`
- [ ] Boolean/null values → `cyan`
- [ ] Comments → `green`

### Integration
- [ ] Detect JSON/YAML in tool results automatically
- [ ] Apply semantic formatting to ToolResultBlock content
- [ ] Preserve indentation and structure
- [ ] Handle nested objects and arrays correctly

---

## Technical Implementation

### Affected Files

**New Files**:
- `src/claude_agent_sdk/rendering/structured_formatter.py`

**Modified Files**:
- `src/claude_agent_sdk/rendering/formatters.py` - Integrate structured formatter

### Implementation

```python
import json
import yaml
from typing import Any

class StructuredDataFormatter:
    """Formats JSON/YAML with semantic type-based coloring."""

    def __init__(self, theme: 'Theme'):
        self.theme = theme

    def format_json(self, data: str) -> str:
        """Format JSON with semantic coloring.

        Args:
            data: JSON string

        Returns:
            ANSI-styled JSON string
        """
        try:
            parsed = json.loads(data)
            return self._format_json_value(parsed, indent=0)
        except json.JSONDecodeError:
            return data  # Return as-is if not valid JSON

    def _format_json_value(self, value: Any, indent: int) -> str:
        """Recursively format JSON value."""
        indent_str = "  " * indent

        if isinstance(value, dict):
            if not value:
                return "{}"

            lines = ["{"]
            items = list(value.items())
            for i, (key, val) in enumerate(items):
                # Key (dim)
                key_styled = self._style(f'"{key}"', 'metadata')
                # Colon (white)
                colon = self._style(': ', 'assistant_message')
                # Value (recursive)
                val_formatted = self._format_json_value(val, indent + 1)

                # Comma (white)
                comma = "," if i < len(items) - 1 else ""

                lines.append(f"{indent_str}  {key_styled}{colon}{val_formatted}{comma}")

            lines.append(f"{indent_str}}}")
            return "\n".join(lines)

        elif isinstance(value, list):
            if not value:
                return "[]"

            lines = ["["]
            for i, item in enumerate(value):
                item_formatted = self._format_json_value(item, indent + 1)
                comma = "," if i < len(value) - 1 else ""
                lines.append(f"{indent_str}  {item_formatted}{comma}")

            lines.append(f"{indent_str}]")
            return "\n".join(lines)

        elif isinstance(value, str):
            # String values (green)
            return self._style(f'"{value}"', 'success')

        elif isinstance(value, bool):
            # Boolean (cyan)
            return self._style(str(value).lower(), 'info')

        elif value is None:
            # Null (cyan)
            return self._style('null', 'info')

        elif isinstance(value, (int, float)):
            # Numbers (green)
            return self._style(str(value), 'success')

        else:
            return str(value)

    def _style(self, text: str, category: str) -> str:
        """Apply ANSI styling."""
        from claude_agent_sdk.rendering.ansi import ANSIEncoder
        style_rule = getattr(self.theme, category)
        encoder = ANSIEncoder()
        return encoder.encode(text, style_rule)

    def detect_format(self, text: str) -> Optional[str]:
        """Detect if text is JSON or YAML.

        Returns:
            "json", "yaml", or None
        """
        text = text.strip()

        # Try JSON first
        if text.startswith(('{', '[')):
            try:
                json.loads(text)
                return "json"
            except json.JSONDecodeError:
                pass

        # Try YAML
        if ':' in text or text.startswith('-'):
            try:
                yaml.safe_load(text)
                return "yaml"
            except yaml.YAMLError:
                pass

        return None
```

---

## Testing Strategy

```python
def test_json_formatting():
    """Test JSON semantic formatting."""
    formatter = StructuredDataFormatter(Theme.claude_code_default())

    json_data = '{"status": "success", "count": 42, "active": true, "error": null}'
    result = formatter.format_json(json_data)

    # Verify keys are dim
    assert_contains_ansi_color(result, '"status"', DIM_GRAY)
    # Verify string values are green
    assert_contains_ansi_color(result, '"success"', BRIGHT_GREEN)
    # Verify numbers are green
    assert_contains_ansi_color(result, '42', BRIGHT_GREEN)
    # Verify booleans are cyan
    assert_contains_ansi_color(result, 'true', BRIGHT_CYAN)
    # Verify null is cyan
    assert_contains_ansi_color(result, 'null', BRIGHT_CYAN)
```

---

**Version**: 1.0 | **Created**: 2025-11-08 | **Priority**: HIGH
