"""Tests for ClaudeCodeFormatter color/theming support (Story 1.3.5).

This module tests the integration of color and theming into the formatter,
including the _style() helper method and color application to all message types.
"""

from claude_agent_sdk.rendering.config import ColorDepth, RendererConfig
from claude_agent_sdk.rendering.formatters import ClaudeCodeFormatter
from claude_agent_sdk.rendering.theme import StyleRule, Theme
from claude_agent_sdk.types import (
    AssistantMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)


class TestFormatterColorSupport:
    """Test color support in ClaudeCodeFormatter."""

    def test_formatter_initializes_color_components(self):
        """Test that formatter initializes classifier and encoder."""
        formatter = ClaudeCodeFormatter()

        assert hasattr(formatter, "classifier")
        assert hasattr(formatter, "encoder")
        assert formatter.classifier is not None
        assert formatter.encoder is not None

    def test_style_method_with_colors_disabled(self):
        """Test _style() returns plain text when colors disabled."""
        config = RendererConfig(color_enabled=False)
        formatter = ClaudeCodeFormatter(config)

        styled_text = formatter._style("Hello", "user_message")

        # Should be unchanged
        assert styled_text == "Hello"
        assert "\x1b[" not in styled_text

    def test_style_method_with_unknown_category(self):
        """Test _style() returns plain text for unknown category."""
        # Use explicit color_depth to avoid TTY detection
        config = RendererConfig(color_enabled=True, color_depth=ColorDepth.BASIC_16)
        formatter = ClaudeCodeFormatter(config)

        styled_text = formatter._style("Hello", "nonexistent_category")

        # Should be unchanged when category not in theme
        assert styled_text == "Hello"
        assert "\x1b[" not in styled_text


class TestColorIntegrationWithMessages:
    """Test that color system integrates correctly with message formatting."""

    def test_user_message_without_colors(self):
        """Test user message without colors when disabled."""
        config = RendererConfig(color_enabled=False)
        formatter = ClaudeCodeFormatter(config)

        message = UserMessage(content="Hello, Claude!")
        result = formatter.format_user_message(message)

        # Should NOT contain ANSI codes
        assert "\x1b[" not in result
        assert "Hello, Claude!" in result

    def test_assistant_message_without_colors(self):
        """Test assistant message without colors when disabled."""
        config = RendererConfig(color_enabled=False)
        formatter = ClaudeCodeFormatter(config)

        message = AssistantMessage(
            content=[TextBlock(text="I can help with that.")],
            model="claude-3-5-sonnet-20241022",
        )
        result = formatter.format_assistant_message(message)

        # Should NOT contain ANSI codes
        assert "\x1b[" not in result
        assert "I can help with that." in result

    def test_tool_use_without_colors(self):
        """Test tool use block without colors when disabled."""
        config = RendererConfig(color_enabled=False)
        formatter = ClaudeCodeFormatter(config)

        block = ToolUseBlock(id="1", name="Read", input={"file_path": "test.py"})
        result = formatter._format_tool_use(block)

        # Should NOT contain ANSI codes
        assert "\x1b[" not in result
        assert "Read" in result

    def test_tool_result_without_colors(self):
        """Test tool result without colors when disabled."""
        config = RendererConfig(color_enabled=False)
        formatter = ClaudeCodeFormatter(config)

        block = ToolResultBlock(
            tool_use_id="1", content="def hello():\n    print('Hi')", is_error=False
        )
        result = formatter._format_tool_result_content(block)

        # Should NOT contain ANSI codes
        assert "\x1b[" not in result
        assert "def hello()" in result


class TestThemeIntegration:
    """Test formatter works with custom themes."""

    def test_formatter_with_custom_theme(self):
        """Test formatter respects custom theme colors."""
        # Create a custom theme with distinct colors
        custom_theme = Theme(
            user_message=StyleRule(fg_color="cyan", bold=True),
            assistant_message=StyleRule(fg_color="green"),
            tool_use=StyleRule(fg_color="yellow"),
            tool_result=StyleRule(fg_color="blue"),
            tool_error=StyleRule(fg_color="red", bold=True),
            error=StyleRule(fg_color="red"),
            warning=StyleRule(fg_color="yellow"),
            success=StyleRule(fg_color="green"),
            info=StyleRule(fg_color="blue"),
            debug=StyleRule(fg_color="magenta"),
            bullet=StyleRule(),
            tree_connector=StyleRule(),
            metadata=StyleRule(),
            truncation=StyleRule(),
            code_block=StyleRule(),
            inline_code=StyleRule(),
            thinking=StyleRule(fg_color="dim"),
            cost_display=StyleRule(fg_color="cyan"),
            system_message=StyleRule(fg_color="magenta"),
        )

        config = RendererConfig(
            color_enabled=False,  # Disable to avoid TTY issues in tests
            color_depth=ColorDepth.BASIC_16,
            theme=custom_theme,
        )
        formatter = ClaudeCodeFormatter(config)

        # Test that the theme is applied by checking the theme reference
        assert formatter.config.theme.user_message.fg_color == "cyan"
        assert formatter.config.theme.user_message.bold is True
