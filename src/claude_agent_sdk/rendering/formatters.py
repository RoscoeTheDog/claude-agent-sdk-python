"""Concrete formatter implementations for message rendering.

This module provides formatters that convert messages to specific output formats.
"""

import re
from typing import Any

from ..types import (
    AssistantMessage,
    ResultMessage,
    StreamEvent,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)
from .ansi import AnsiEncoder
from .base import Formatter
from .classifier import BlockClassifier
from .config import RendererConfig, RenderLevel


class ClaudeCodeFormatter(Formatter):
    """Formatter that matches Claude Code CLI UTF-8 rendering style.

    This formatter produces output matching the exact format used by the
    Claude Code CLI, including:
    - Bullet points (●) for messages
    - Tree connectors (⎿) for indented content
    - Parameter formatting (quoted strings, unquoted non-strings)
    - Truncation indicators with ctrl+o hint

    Example output:
        ● User: Hello, how are you?

        ● I'm doing well, thank you!

        ● Read(file_path: "test.py", limit: 100)
          ⎿  def hello():
                 print("Hello")
             ... +5 lines (ctrl+o to expand)

        ● Result ended
          Cost: $0.0042
    """

    def __init__(self, config: RendererConfig | None = None) -> None:
        """Initialize formatter with configuration.

        Args:
            config: Rendering configuration. If None, uses default RendererConfig
                   with Claude Code CLI UTF-8 characters.
        """
        super().__init__(config)
        self.classifier = BlockClassifier()
        self.encoder = AnsiEncoder(color_depth=self.config.color_depth)

        # Initialize syntax highlighter if enabled and theme has semantic_mapping (Story 4)
        if self.config.enable_syntax_highlighting and self.config.theme.semantic_mapping:
            from .syntax import SyntaxHighlighter
            self.syntax_highlighter: SyntaxHighlighter | None = SyntaxHighlighter(
                theme=self.config.theme,
                semantic_mapping=self.config.theme.semantic_mapping,
                enabled=True
            )
        else:
            self.syntax_highlighter = None

    def _style(self, text: str, category: str) -> str:
        """Apply color styling to text based on semantic category.

        Args:
            text: The text to style
            category: Semantic category name (e.g., "user_message", "error", "tool_use")

        Returns:
            Styled text with ANSI escape codes if colors enabled, otherwise unchanged text.
        """
        if not self.config.color_enabled:
            return text

        # Get the StyleRule for this category from the theme
        style_rule = getattr(self.config.theme, category, None)
        if style_rule is None:
            # Category not found in theme, return unstyled text
            return text

        # Encode the text with the style rule
        return self.encoder.encode(text, style_rule)

    def format_user_message(self, message: UserMessage) -> str:
        """Format a user message.

        Formats:
        - Simple text: "● User: <text>"
        - Structured content: Multi-line with bullets and tree connectors

        Args:
            message: UserMessage to format

        Returns:
            Formatted string
        """
        bullet = self._style(self.config.bullet, "bullet")

        # Simple string content
        if isinstance(message.content, str):
            label = self._style("User:", "user_message")
            return f"{bullet} {label} {message.content}"

        # Structured content (list of blocks)
        lines = []

        # Check if this is an answer to questions (tool result response)
        if message.parent_tool_use_id:
            label = self._style("User answered Claude's questions:", "user_message")
            lines.append(f"{bullet} {label}")
        else:
            label = self._style("User:", "user_message")
            lines.append(f"{bullet} {label}")

        # Format each content block
        for block in message.content:
            if isinstance(block, TextBlock):
                # Indent the text content
                text_lines = block.text.split("\n")
                for line in text_lines:
                    lines.append(f"  {line}")
            elif isinstance(block, ToolResultBlock):
                # Format tool result in user message
                lines.append(self._format_tool_result_content(block))

        return "\n".join(lines)

    def format_assistant_message(self, message: AssistantMessage) -> str:
        """Format an assistant message respecting render_level.

        Formats:
        - Text blocks: "● <text>" (all levels)
        - Thinking blocks: "● <thinking text>" (all levels)
        - Tool use blocks: "● <tool>(<params>)" (STANDARD+)
        - Tool result blocks: "  ⎿ <output>" (DETAILED+)

        Render level behavior:
        - MINIMAL: Only text and thinking blocks
        - STANDARD: + tool use blocks (no outputs)
        - DETAILED: + tool result blocks

        Args:
            message: AssistantMessage to format

        Returns:
            Formatted string
        """
        lines = []
        bullet = self._style(self.config.bullet, "bullet")

        for block in message.content:
            if isinstance(block, TextBlock):
                # Always show text (all levels)
                styled_text = self._style(block.text, "assistant_message")
                lines.append(f"{bullet} {styled_text}")

            elif isinstance(block, ThinkingBlock):
                # Always show thinking (all levels)
                styled_thinking = self._style(block.thinking, "thinking")
                lines.append(f"{bullet} {styled_thinking}")

            elif (
                isinstance(block, ToolUseBlock)
                and self.config.render_level >= RenderLevel.STANDARD
            ):
                # Show tool use at STANDARD level and above
                formatted_tool = self._format_tool_use(block)
                lines.append(formatted_tool)
                # MINIMAL level: skip tool use blocks

            elif (
                isinstance(block, ToolResultBlock)
                and self.config.render_level >= RenderLevel.DETAILED
            ):
                # Show tool results at DETAILED level and above
                formatted_result = self._format_tool_result_content(block)
                lines.append(formatted_result)
                # MINIMAL/STANDARD: skip tool results

        return "\n".join(lines)

    def format_system_message(self, message: SystemMessage) -> str:
        """Format a system message.

        Basic bullet format (only rendered at DEBUG+ levels).

        Args:
            message: SystemMessage to format

        Returns:
            Formatted string
        """
        # Format: ● System: <subtype>
        bullet = self._style(self.config.bullet, "bullet")
        label = self._style(f"System: {message.subtype}", "system_message")
        return f"{bullet} {label}"

    def format_result_message(self, message: ResultMessage) -> str:
        """Format a result message.

        Format:
            ● Result ended
              Cost: $<total_cost_usd>  (only if show_cost=True)

        Args:
            message: ResultMessage to format

        Returns:
            Formatted string
        """
        bullet = self._style(self.config.bullet, "bullet")
        result_text = self._style("Result ended", "info")
        lines = [f"{bullet} {result_text}"]

        # Only show cost if enabled and available
        if self.config.show_cost and message.total_cost_usd is not None:
            cost_text = self._style(
                f"Cost: ${message.total_cost_usd:.4f}", "cost_display"
            )
            lines.append(f"  {cost_text}")

        return "\n".join(lines)

    def format_stream_event(self, message: StreamEvent) -> str:
        """Format a stream event.

        Basic rendering for Sprint 1. More sophisticated incremental
        updates will be added in Sprint 2.

        Args:
            message: StreamEvent to format

        Returns:
            Formatted string (currently basic event representation)
        """
        # Basic representation for now
        event_type = message.event.get("type", "unknown")
        return f"{self.config.bullet} Stream: {event_type}"

    def _format_tool_use(self, block: ToolUseBlock, state: str = "active") -> str:
        """Format a tool use block with component-level styling.

        This method implements component-level styling where each part
        of the tool call (bullet, name, parameters) is styled independently.
        State-based bullet coloring provides visual feedback about tool execution.

        Format: <bullet> <name>(<key>: <value>, ...)

        Args:
            block: ToolUseBlock to format
            state: Tool state for bullet coloring:
                   - "active": Green bullet (tool succeeded)
                   - "pending": White bullet (tool not yet executed)
                   - "failed": Red bullet (tool execution failed)

        Returns:
            Formatted tool use string with component-level styling

        Example:
            >>> # Active tool (green bullet):
            >>> "● read_file(path: "/src/main.py", lines: 100)"
            >>> # Where ● is green, parameters are styled by type
        """
        # State-based bullet coloring
        bullet_map = {
            "active": self._style(self.config.bullet, "success"),  # Green
            "pending": self._style(self.config.bullet, "assistant_message"),  # White
            "failed": self._style(self.config.bullet, "error"),  # Red
        }
        bullet = bullet_map.get(state, bullet_map["pending"])

        # Tool name (white, like assistant message)
        tool_name = self._style(block.name, "assistant_message")

        # Format parameters with component-level styling
        param_parts = []
        for key, value in block.input.items():
            # Parameter key (white)
            key_styled = self._style(f"{key}: ", "assistant_message")

            # Parameter value (type-based coloring)
            formatted_value = self._format_parameter_value(value)
            if isinstance(value, str):
                # String values in green for visibility
                value_styled = self._style(formatted_value, "success")
            elif isinstance(value, bool):
                # Boolean in cyan
                value_styled = self._style(formatted_value, "info")
            elif isinstance(value, (int, float)):
                # Numbers in green
                value_styled = self._style(formatted_value, "success")
            elif value is None:
                # Null in cyan
                value_styled = self._style(formatted_value, "info")
            else:
                # Complex types (list, dict) as JSON in success color
                value_styled = self._style(formatted_value, "success")

            param_parts.append(key_styled + value_styled)

        # Join parameters
        params_str = ", ".join(param_parts) if param_parts else ""

        # Parentheses (white, like assistant message)
        open_paren = self._style("(", "assistant_message")
        close_paren = self._style(")", "assistant_message")

        return f"{bullet} {tool_name}{open_paren}{params_str}{close_paren}"

    def _format_parameter_value(self, value: Any) -> str:
        """Format a parameter value with appropriate quoting.

        Args:
            value: Parameter value to format

        Returns:
            Formatted value string (quoted if string, unquoted otherwise)
        """
        if isinstance(value, str):
            # Quote strings, escape internal quotes
            escaped = value.replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(value, bool):
            # Python bool to lowercase
            return str(value).lower()
        elif value is None:
            return "null"
        elif isinstance(value, (list, dict)):
            # For complex types, use a compact representation
            import json

            return json.dumps(value, ensure_ascii=False)
        else:
            # Numbers and other types
            return str(value)

    def _estimate_token_count(self, content: Any) -> int:
        """Estimate token count for tool result content.

        Uses a rough estimation of 1 token ≈ 4 characters.
        This is sufficient for warning detection without requiring
        a full tokenizer dependency.

        Args:
            content: Tool result content (str, dict, list, or None)

        Returns:
            Estimated token count
        """
        if content is None:
            return 0
        elif isinstance(content, str):
            return len(content) // 4
        else:
            # For complex types, convert to JSON first
            import json
            content_str = json.dumps(content, ensure_ascii=False)
            return len(content_str) // 4

    def _format_tool_result_warning(self, content_size: int) -> str:
        """Generate warning for large tool results.

        Displays a warning when tool results exceed 10,000 tokens (~40KB text),
        as large MCP responses can quickly fill up context windows.

        Args:
            content_size: Size of result content in tokens (approximate)

        Returns:
            Formatted warning string or empty string if no warning needed
        """
        if content_size > 10000:
            warning_icon = self._style("⚠️", "warning")
            warning_text = self._style(
                f" Large MCP response (~{content_size/1000:.1f}k tokens), "
                f"this can fill up context quickly",
                "warning"
            )
            return f"  {warning_icon}{warning_text}\n"
        return ""

    def _format_tool_result_content(self, block: ToolResultBlock) -> str:
        """Format tool result content with tree connector and indentation.

        Format:
          ⚠️ Large MCP response (...)  [if > 10k tokens]
          ⎿  <first line>
             <second line>
             ... +N lines (ctrl+o to expand)

        Args:
            block: ToolResultBlock to format

        Returns:
            Formatted tool result string
        """

        # Handle different content types
        if block.content is None:
            content_str = ""
        elif isinstance(block.content, str):
            content_str = block.content
        else:
            # List of content blocks
            import json

            content_str = json.dumps(block.content, ensure_ascii=False, indent=2)

        # Check if we need a warning for large responses
        token_count = self._estimate_token_count(block.content)
        warning = self._format_tool_result_warning(token_count)

        # Try syntax highlighting for structured data (Story 4)
        # Only highlight non-empty, non-error content
        if self.syntax_highlighter and not block.is_error and content_str:
            highlighted = self.syntax_highlighter.highlight(
                content_str,
                language_hint=None,  # Auto-detect JSON/YAML
                context="tool_result"
            )
            # Only use highlighted version if it's different (formatting was applied)
            if highlighted != content_str:
                content_str = highlighted

        # Determine semantic category based on error status
        category = "tool_error" if block.is_error else "tool_result"

        # Add error prefix if needed
        if block.is_error:
            content_str = f"ERROR: {content_str}"

        # Truncate if needed
        if (
            self.config.max_tool_output_length
            and len(content_str) > self.config.max_tool_output_length
        ):
            content_str = self._truncate_text(
                content_str,
                self.config.max_tool_output_length,
                f"{self.config.ellipsis} +{{n}} lines (ctrl+o to expand)",
            )

        # Format with tree connector and indentation
        tree_connector = self._style(self.config.tree_connector, "tree_connector")
        if not content_str:
            empty_text = self._style("(empty)", category)
            return f"  {tree_connector}  {empty_text}"

        lines = content_str.split("\n")
        formatted_lines = []

        # Calculate indent for continuation lines
        # Indent = 2 spaces + tree_connector width + 2 spaces
        indent = " " * (2 + len(self.config.tree_connector) + 2)

        for i, line in enumerate(lines):
            # Strip line numbers for clean display (matching Claude Code CLI behavior)
            # Pattern: "     20→    print()" -> "    print()"
            # Removes CLI-added whitespace + line number, preserves content indentation
            cleaned_line = re.sub(r"^\s*\d+→", "", line)

            if i == 0:
                # First line uses tree connector with styled content
                styled_line = self._style(cleaned_line, category)
                formatted_lines.append(f"  {tree_connector}  {styled_line}")
            else:
                # Continuation lines align with first line content with styled content
                styled_line = self._style(cleaned_line, category)
                formatted_lines.append(f"{indent}{styled_line}")

        result = "\n".join(formatted_lines)

        # Prepend warning if needed
        if warning:
            result = warning + result

        return result
