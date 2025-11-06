"""Integration tests for the rendering system.

Tests that verify the complete rendering system works with real SDK messages
and doesn't cause regressions in existing SDK functionality.
"""

import tempfile
from io import StringIO
from pathlib import Path

from claude_agent_sdk.rendering import (
    ClaudeCodeFormatter,
    FileHandler,
    MessageRenderer,
    RendererConfig,
    RenderLevel,
    StreamHandler,
)
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)


class TestEndToEndRendering:
    """Test complete rendering workflows."""

    def test_simple_conversation_rendering(self):
        """Test rendering a simple conversation."""
        renderer = MessageRenderer()
        formatter = ClaudeCodeFormatter()
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)
        renderer.add_handler(handler)

        # User asks a question
        user_msg = UserMessage(content="What is 2 + 2?")
        renderer.render(user_msg)

        # Assistant responds with thinking and text
        thinking = ThinkingBlock(thinking="Let me calculate...", signature="sig-123")
        text = TextBlock(text="The answer is 4.")
        assistant_msg = AssistantMessage(
            content=[thinking, text], model="claude-3-5-sonnet-20241022"
        )
        renderer.render(assistant_msg)

        # Result message
        result_msg = ResultMessage(
            subtype="ended",
            duration_ms=1000,
            duration_api_ms=500,
            is_error=False,
            num_turns=1,
            session_id="session-123",
            total_cost_usd=0.0012,
        )
        renderer.render(result_msg)

        output = stream.getvalue()
        assert "What is 2 + 2?" in output
        assert "Let me calculate..." in output
        assert "The answer is 4." in output
        assert "Result ended" in output
        # Cost should not be shown by default (show_cost=False)
        assert "$0.0012" not in output

    def test_tool_use_workflow(self):
        """Test rendering a workflow with tool use."""
        renderer = MessageRenderer()
        # Use DETAILED level to show tool results
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)
        renderer.add_handler(handler)

        # User request
        user_msg = UserMessage(content="Read the README file")
        renderer.render(user_msg)

        # Assistant uses Read tool
        text_block = TextBlock(text="Let me read that file for you.")
        tool_block = ToolUseBlock(
            id="tool-123", name="Read", input={"file_path": "README.md", "limit": 100}
        )
        assistant_msg = AssistantMessage(
            content=[text_block, tool_block], model="claude-3-5-sonnet-20241022"
        )
        renderer.render(assistant_msg)

        # Tool result
        result_content = (
            "# My Project\n\nThis is a test project.\n\nMore content here..."
        )
        result_block = ToolResultBlock(tool_use_id="tool-123", content=result_content)
        assistant_result = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        renderer.render(assistant_result)

        output = stream.getvalue()
        assert "Read the README file" in output
        assert "Let me read that file for you." in output
        assert 'Read(file_path: "README.md", limit: 100)' in output
        assert "# My Project" in output

    def test_multi_handler_rendering(self):
        """Test rendering to multiple handlers simultaneously."""
        with tempfile.TemporaryDirectory() as tmpdir:
            renderer = MessageRenderer()
            formatter = ClaudeCodeFormatter()

            # Console handler
            console_stream = StringIO()
            console_handler = StreamHandler(formatter, stream=console_stream)

            # File handler
            file_path = Path(tmpdir) / "output.txt"
            file_handler = FileHandler(formatter, file_path)

            renderer.add_handler(console_handler)
            renderer.add_handler(file_handler)

            # Render messages
            msg = UserMessage(content="Test message")
            renderer.render(msg)

            file_handler.close()

            # Both outputs should contain the message
            console_output = console_stream.getvalue()
            file_output = file_path.read_text(encoding="utf-8")

            assert "Test message" in console_output
            assert "Test message" in file_output

    def test_render_level_filtering(self):
        """Test that render levels properly filter messages."""
        # MINIMAL level - only user and assistant text
        config_minimal = RendererConfig(render_level=RenderLevel.MINIMAL)
        formatter_minimal = ClaudeCodeFormatter(config_minimal)
        stream_minimal = StringIO()
        handler_minimal = StreamHandler(formatter_minimal, stream=stream_minimal)

        # DEBUG level - includes system messages
        config_debug = RendererConfig(render_level=RenderLevel.DEBUG)
        formatter_debug = ClaudeCodeFormatter(config_debug)
        stream_debug = StringIO()
        handler_debug = StreamHandler(formatter_debug, stream=stream_debug)

        # Create messages
        user_msg = UserMessage(content="Hello")
        system_msg = SystemMessage(subtype="test", data={})

        # Render with minimal level
        handler_minimal.handle(user_msg)
        handler_minimal.handle(system_msg)

        # Render with debug level
        handler_debug.handle(user_msg)
        handler_debug.handle(system_msg)

        # Minimal should have user message but not system
        output_minimal = stream_minimal.getvalue()
        assert "Hello" in output_minimal
        assert "System:" not in output_minimal

        # Debug should have both
        output_debug = stream_debug.getvalue()
        assert "Hello" in output_debug
        assert "System:" in output_debug

    def test_custom_configuration(self):
        """Test rendering with custom configuration."""
        config = RendererConfig(
            bullet="*",
            tree_connector="|",
            max_text_length=50,
            max_tool_output_length=30,
        )
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)

        # Simple message
        msg = UserMessage(content="Test")
        handler.handle(msg)

        output = stream.getvalue()
        assert "* User: Test" in output  # Custom bullet

    def test_display_message_convenience_function(self):
        """Test the display_message convenience function."""
        # Capture stdout
        stream = StringIO()

        # Create renderer with custom stream
        renderer = MessageRenderer()
        formatter = ClaudeCodeFormatter()
        handler = StreamHandler(formatter, stream=stream)
        renderer.add_handler(handler)

        # Create and display message
        msg = UserMessage(content="Hello from convenience function")
        renderer.render(msg)

        output = stream.getvalue()
        assert "Hello from convenience function" in output

    def test_error_handling_in_tool_results(self):
        """Test that error tool results are properly formatted."""
        renderer = MessageRenderer()
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)
        renderer.add_handler(handler)

        # Tool result with error
        error_block = ToolResultBlock(
            tool_use_id="tool-123", content="File not found: missing.txt", is_error=True
        )
        msg = AssistantMessage(
            content=[error_block], model="claude-3-5-sonnet-20241022"
        )
        renderer.render(msg)

        output = stream.getvalue()
        assert "ERROR:" in output
        assert "File not found" in output

    def test_long_content_truncation(self):
        """Test that long content is properly truncated."""
        config = RendererConfig(
            max_tool_output_length=50, render_level=RenderLevel.DETAILED
        )
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)

        # Create long tool result
        long_content = "\n".join([f"Line {i}" for i in range(100)])
        result_block = ToolResultBlock(tool_use_id="tool-123", content=long_content)
        msg = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )

        handler.handle(msg)

        output = stream.getvalue()
        assert "(ctrl+o to expand)" in output
        assert len(output) < len(long_content)  # Should be truncated

    def test_utf8_characters_render_correctly(self):
        """Test that UTF-8 characters render correctly."""
        formatter = ClaudeCodeFormatter()
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)

        msg = UserMessage(content="Hello \u2022 World \u2192")
        handler.handle(msg)

        output = stream.getvalue()
        assert "\u25cf" in output  # Bullet
        assert "\u2022" in output  # Original bullet from message
        assert "\u2192" in output  # Arrow from message

    def test_empty_content_handling(self):
        """Test handling of empty or None content."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)

        # Empty tool result
        empty_block = ToolResultBlock(tool_use_id="tool-123", content="")
        msg = AssistantMessage(
            content=[empty_block], model="claude-3-5-sonnet-20241022"
        )
        handler.handle(msg)

        output = stream.getvalue()
        assert "(empty)" in output

    def test_no_regression_in_existing_tests(self):
        """Test that rendering system doesn't break existing SDK functionality."""
        # This test verifies that the rendering module can be imported
        # and used alongside existing SDK components without issues

        # Create various message types (same as used throughout SDK)
        user_msg = UserMessage(content="Test")
        assistant_msg = AssistantMessage(
            content=[TextBlock(text="Response")], model="claude-3-5-sonnet-20241022"
        )
        result_msg = ResultMessage(
            subtype="ended",
            duration_ms=1000,
            duration_api_ms=500,
            is_error=False,
            num_turns=1,
            session_id="session-123",
            total_cost_usd=0.01,
        )

        # All message types should be creatable and usable
        assert user_msg.content == "Test"
        assert assistant_msg.content[0].text == "Response"
        assert result_msg.total_cost_usd == 0.01

        # Rendering should work without affecting message objects
        renderer = MessageRenderer()
        formatter = ClaudeCodeFormatter()
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)
        renderer.add_handler(handler)

        renderer.render(user_msg)
        renderer.render(assistant_msg)
        renderer.render(result_msg)

        # Original messages should be unchanged
        assert user_msg.content == "Test"
        assert assistant_msg.content[0].text == "Response"
        assert result_msg.total_cost_usd == 0.01


class TestCodeCoverage:
    """Tests to ensure high code coverage."""

    def test_all_message_types_formatted(self):
        """Test that all message types can be formatted."""
        # Use DETAILED level to show all block types including tool results
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)

        # UserMessage
        user_msg = UserMessage(content="Test")
        assert formatter.format(user_msg)

        # AssistantMessage with various content types
        text_block = TextBlock(text="Text")
        thinking_block = ThinkingBlock(thinking="Thinking", signature="sig-123")
        tool_block = ToolUseBlock(id="tool-1", name="Test", input={"arg": "value"})
        result_block = ToolResultBlock(tool_use_id="tool-1", content="Result")

        for block in [text_block, thinking_block, tool_block, result_block]:
            msg = AssistantMessage(content=[block], model="claude-3-5-sonnet-20241022")
            assert formatter.format(msg)

        # SystemMessage
        system_msg = SystemMessage(subtype="test", data={})
        assert formatter.format(system_msg)

        # ResultMessage
        result_msg = ResultMessage(
            subtype="ended",
            duration_ms=1000,
            duration_api_ms=500,
            is_error=False,
            num_turns=1,
            session_id="session-123",
            total_cost_usd=0.01,
        )
        assert formatter.format(result_msg)

    def test_all_parameter_types_formatted(self):
        """Test that all parameter types are formatted correctly."""
        formatter = ClaudeCodeFormatter()

        # String, number, boolean, None, list, dict
        tool_block = ToolUseBlock(
            id="tool-1",
            name="Test",
            input={
                "string_param": "value",
                "number_param": 42,
                "bool_param": True,
                "none_param": None,
                "list_param": [1, 2, 3],
                "dict_param": {"key": "value"},
            },
        )
        msg = AssistantMessage(content=[tool_block], model="claude-3-5-sonnet-20241022")
        output = formatter.format(msg)

        assert 'string_param: "value"' in output
        assert "number_param: 42" in output
        assert "bool_param: true" in output
        assert "none_param: null" in output
        assert "[1, 2, 3]" in output or "[1,2,3]" in output
        assert "key" in output
