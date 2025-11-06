"""Concrete formatter implementations for message rendering.

This module provides formatters that convert messages to specific output formats.
"""

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
from .base import Formatter
from .config import RendererConfig


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
        # Simple string content
        if isinstance(message.content, str):
            return f"{self.config.bullet} User: {message.content}"

        # Structured content (list of blocks)
        lines = []

        # Check if this is an answer to questions (tool result response)
        if message.parent_tool_use_id:
            lines.append(f"{self.config.bullet} User answered Claude's questions:")
        else:
            lines.append(f"{self.config.bullet} User:")

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
        """Format an assistant message.

        Formats:
        - Text blocks: "● <text>"
        - Tool use blocks: "● <tool>(<params>)"
        - Thinking blocks: "● <thinking text>"

        Args:
            message: AssistantMessage to format

        Returns:
            Formatted string
        """
        lines = []

        for block in message.content:
            if isinstance(block, TextBlock):
                # Simple text with bullet
                lines.append(f"{self.config.bullet} {block.text}")

            elif isinstance(block, ThinkingBlock):
                # Thinking block - render the thinking text
                lines.append(f"{self.config.bullet} {block.thinking}")

            elif isinstance(block, ToolUseBlock):
                # Format: ● <tool>(<params>)
                formatted_tool = self._format_tool_use(block)
                lines.append(formatted_tool)

            elif isinstance(block, ToolResultBlock):
                # Format tool result
                formatted_result = self._format_tool_result_content(block)
                lines.append(formatted_result)

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
        return f"{self.config.bullet} System: {message.subtype}"

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
        lines = [f"{self.config.bullet} Result ended"]

        # Only show cost if enabled and available
        if self.config.show_cost and message.total_cost_usd is not None:
            lines.append(f"  Cost: ${message.total_cost_usd:.4f}")

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

    def _format_tool_use(self, block: ToolUseBlock) -> str:
        """Format a tool use block.

        Format: ● <name>(<key>: "value", <key>: value)
        - String parameters are quoted
        - Other parameters are not quoted
        - MCP tools can optionally be labeled (future enhancement)

        Args:
            block: ToolUseBlock to format

        Returns:
            Formatted tool use string
        """
        # Format parameters
        param_strs = []
        for key, value in block.input.items():
            formatted_value = self._format_parameter_value(value)
            param_strs.append(f"{key}: {formatted_value}")

        params = ", ".join(param_strs)

        # Format: ● <tool>(<params>)
        return f"{self.config.bullet} {block.name}({params})"

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

    def _format_tool_result_content(self, block: ToolResultBlock) -> str:
        """Format tool result content with tree connector and indentation.

        Format:
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
        if not content_str:
            return f"  {self.config.tree_connector}  (empty)"

        lines = content_str.split("\n")
        formatted_lines = []

        for i, line in enumerate(lines):
            if i == 0:
                # First line uses tree connector
                formatted_lines.append(f"  {self.config.tree_connector}  {line}")
            else:
                # Continuation lines use regular indent
                formatted_lines.append(f"     {line}")

        return "\n".join(formatted_lines)
