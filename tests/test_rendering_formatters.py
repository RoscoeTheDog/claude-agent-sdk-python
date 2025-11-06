"""Tests for message formatters."""

from claude_agent_sdk.rendering import ClaudeCodeFormatter, RendererConfig, RenderLevel
from claude_agent_sdk.types import (
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


class TestClaudeCodeFormatter:
    """Test ClaudeCodeFormatter rendering."""

    def test_formatter_uses_default_config(self):
        """Test that formatter uses default config if none provided."""
        formatter = ClaudeCodeFormatter()
        assert formatter.config is not None
        assert formatter.config.bullet == "\u25cf"

    def test_formatter_uses_custom_config(self):
        """Test that formatter uses provided config."""
        config = RendererConfig(bullet="*", tree_connector="|")
        formatter = ClaudeCodeFormatter(config)
        assert formatter.config.bullet == "*"
        assert formatter.config.tree_connector == "|"

    def test_format_user_message_simple_text(self):
        """Test formatting simple user message with text content."""
        formatter = ClaudeCodeFormatter()
        message = UserMessage(content="Hello, Claude!")
        result = formatter.format_user_message(message)
        assert result == "\u25cf User: Hello, Claude!"

    def test_format_user_message_with_custom_bullet(self):
        """Test user message formatting with custom bullet."""
        config = RendererConfig(bullet="*")
        formatter = ClaudeCodeFormatter(config)
        message = UserMessage(content="Hello!")
        result = formatter.format_user_message(message)
        assert result == "* User: Hello!"

    def test_format_user_message_structured_content(self):
        """Test formatting user message with structured content blocks."""
        formatter = ClaudeCodeFormatter()
        text_block = TextBlock(text="This is my question")
        message = UserMessage(content=[text_block])
        result = formatter.format_user_message(message)
        expected = "\u25cf User:\n  This is my question"
        assert result == expected

    def test_format_user_message_answer_to_questions(self):
        """Test formatting user message that answers Claude's questions."""
        formatter = ClaudeCodeFormatter()
        text_block = TextBlock(text="Yes")
        message = UserMessage(content=[text_block], parent_tool_use_id="tool-123")
        result = formatter.format_user_message(message)
        expected = "\u25cf User answered Claude's questions:\n  Yes"
        assert result == expected

    def test_format_user_message_multiline_text(self):
        """Test user message with multiline text content."""
        formatter = ClaudeCodeFormatter()
        text_block = TextBlock(text="Line 1\nLine 2\nLine 3")
        message = UserMessage(content=[text_block])
        result = formatter.format_user_message(message)
        expected = "\u25cf User:\n  Line 1\n  Line 2\n  Line 3"
        assert result == expected

    def test_format_assistant_message_with_text(self):
        """Test formatting assistant message with text content."""
        formatter = ClaudeCodeFormatter()
        text_block = TextBlock(text="Hello, human!")
        message = AssistantMessage(
            content=[text_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert result == "\u25cf Hello, human!"

    def test_format_assistant_message_with_thinking(self):
        """Test formatting assistant message with thinking block."""
        formatter = ClaudeCodeFormatter()
        thinking_block = ThinkingBlock(
            thinking="Let me analyze this...", signature="sig-123"
        )
        message = AssistantMessage(
            content=[thinking_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert result == "\u25cf Let me analyze this..."

    def test_format_assistant_message_with_tool_use(self):
        """Test formatting assistant message with tool use."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool-123", name="Read", input={"file_path": "test.py"}
        )
        message = AssistantMessage(
            content=[tool_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert result == '\u25cf Read(file_path: "test.py")'

    def test_format_assistant_message_multiple_blocks(self):
        """Test formatting assistant message with multiple content blocks."""
        formatter = ClaudeCodeFormatter()
        text_block = TextBlock(text="Let me check that file.")
        tool_block = ToolUseBlock(
            id="tool-123", name="Read", input={"file_path": "test.py"}
        )
        message = AssistantMessage(
            content=[text_block, tool_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        expected = '\u25cf Let me check that file.\n\u25cf Read(file_path: "test.py")'
        assert result == expected

    def test_format_tool_use_string_parameters(self):
        """Test that string parameters are quoted in tool use."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool-123",
            name="Read",
            input={"file_path": "test.py", "encoding": "utf-8"},
        )
        message = AssistantMessage(
            content=[tool_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert 'file_path: "test.py"' in result
        assert 'encoding: "utf-8"' in result

    def test_format_tool_use_non_string_parameters(self):
        """Test that non-string parameters are not quoted in tool use."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(id="tool-123", name="Read", input={"limit": 100})
        message = AssistantMessage(
            content=[tool_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert "limit: 100" in result
        assert '"100"' not in result

    def test_format_tool_use_boolean_parameters(self):
        """Test that boolean parameters are lowercase."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool-123",
            name="Search",
            input={"recursive": True, "case_sensitive": False},
        )
        message = AssistantMessage(
            content=[tool_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert "recursive: true" in result
        assert "case_sensitive: false" in result

    def test_format_tool_use_null_parameters(self):
        """Test that None parameters are rendered as null."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(id="tool-123", name="Process", input={"config": None})
        message = AssistantMessage(
            content=[tool_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert "config: null" in result

    def test_format_tool_use_list_parameters(self):
        """Test that list parameters are JSON-formatted."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool-123", name="Process", input={"items": [1, 2, 3]}
        )
        message = AssistantMessage(
            content=[tool_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert "items: [1, 2, 3]" in result or "items: [1,2,3]" in result

    def test_format_tool_use_dict_parameters(self):
        """Test that dict parameters are JSON-formatted."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool-123", name="Process", input={"config": {"key": "value"}}
        )
        message = AssistantMessage(
            content=[tool_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert '"key": "value"' in result or '"key":"value"' in result

    def test_format_tool_use_escaped_quotes(self):
        """Test that quotes in string parameters are escaped."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool-123", name="Echo", input={"text": 'He said "hello"'}
        )
        message = AssistantMessage(
            content=[tool_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert 'text: "He said \\"hello\\""' in result

    def test_format_tool_result_simple_text(self):
        """Test formatting tool result with simple text."""
        # Use DETAILED level to show tool results
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)
        result_block = ToolResultBlock(
            tool_use_id="tool-123", content="File contents here"
        )
        message = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        expected = "  \u23bf  File contents here"
        assert expected in result

    def test_format_tool_result_multiline_text(self):
        """Test formatting tool result with multiline text."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)
        result_block = ToolResultBlock(
            tool_use_id="tool-123", content="Line 1\nLine 2\nLine 3"
        )
        message = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert "  \u23bf  Line 1" in result
        assert "     Line 2" in result
        assert "     Line 3" in result

    def test_format_tool_result_error(self):
        """Test formatting tool result with error."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)
        result_block = ToolResultBlock(
            tool_use_id="tool-123", content="File not found", is_error=True
        )
        message = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert "ERROR: File not found" in result

    def test_format_tool_result_empty_content(self):
        """Test formatting tool result with empty content."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)
        result_block = ToolResultBlock(tool_use_id="tool-123", content="")
        message = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert "(empty)" in result

    def test_format_tool_result_none_content(self):
        """Test formatting tool result with None content."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)
        result_block = ToolResultBlock(tool_use_id="tool-123", content=None)
        message = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert "(empty)" in result

    def test_format_tool_result_truncation(self):
        """Test that long tool results are truncated with indicator."""
        config = RendererConfig(
            max_tool_output_length=20, render_level=RenderLevel.DETAILED
        )
        formatter = ClaudeCodeFormatter(config)
        long_content = "x" * 50 + "\n" + "y" * 50
        result_block = ToolResultBlock(tool_use_id="tool-123", content=long_content)
        message = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)
        assert "(ctrl+o to expand)" in result
        assert len(result) < len(long_content) + 100  # Should be truncated

    def test_format_tool_result_strips_line_number_whitespace(self):
        """Test that extra whitespace before line numbers is stripped."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)

        # Simulate CLI output with extra whitespace before line numbers
        # Current: "     1→# Header" (7 spaces total before "1")
        # Expected: "  ⎿  1→# Header" (2 + ⎿ + 2 spaces before "1")
        content_with_spaces = "     1→# Header\n     2→Content\n     3→More"

        result_block = ToolResultBlock(
            tool_use_id="tool-123", content=content_with_spaces
        )
        message = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)

        # First line should have: 2 spaces + tree_connector + 2 spaces + "1→..."
        # Continuation lines should align properly
        assert "  \u23bf  1→# Header" in result
        assert "     2→Content" in result  # 5 spaces (2 + 1 + 2)
        assert "     3→More" in result

    def test_format_tool_result_preserves_non_line_number_whitespace(self):
        """Test that indentation NOT part of line numbers is preserved."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)

        # Content with meaningful indentation (not line numbers)
        # This is the indentation WITHIN the content, like code blocks
        content_with_indent = "def foo():\n    return 42\n        nested"

        result_block = ToolResultBlock(
            tool_use_id="tool-123", content=content_with_indent
        )
        message = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)

        # Should preserve the 4-space indent for "return 42"
        # and the 8-space indent for "nested"
        assert "    return 42" in result
        assert "        nested" in result

    def test_format_tool_result_preserves_indentation_after_line_numbers(self):
        """Test that indentation after line numbers (→) is preserved."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)

        # CLI output format: "     1→# Header" and "     7→   - List item"
        # The spaces AFTER → are meaningful indentation that must be preserved
        content_with_line_numbers = (
            "     1→# Claude Agent SDK Examples\n"
            "     2→\n"
            "     3→This folder contains examples.\n"
            "     4→\n"
            "     5→## Available Examples\n"
            "     6→\n"
            "     7→   - **[Pretty Printer Demos]** - Message rendering (NEW!)\n"
            "     8→      - More indented item"
        )

        result_block = ToolResultBlock(
            tool_use_id="tool-123", content=content_with_line_numbers
        )
        message = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)

        # Should strip the leading whitespace before line numbers
        # but preserve indentation AFTER the arrow
        assert "7→   - **[Pretty Printer Demos]**" in result  # 3 spaces after →
        assert "8→      - More indented item" in result  # 6 spaces after →

    def test_format_system_message(self):
        """Test formatting system message."""
        formatter = ClaudeCodeFormatter()
        message = SystemMessage(subtype="usage_limit_exceeded", data={})
        result = formatter.format_system_message(message)
        assert result == "\u25cf System: usage_limit_exceeded"

    def test_format_result_message_with_cost_default(self):
        """Test formatting result message with cost (default show_cost=False)."""
        formatter = ClaudeCodeFormatter()
        message = ResultMessage(
            subtype="ended",
            duration_ms=1000,
            duration_api_ms=500,
            is_error=False,
            num_turns=1,
            session_id="session-123",
            total_cost_usd=0.0042,
        )
        result = formatter.format_result_message(message)
        # Cost should be hidden by default
        assert result == "\u25cf Result ended"
        assert "Cost" not in result

    def test_format_result_message_with_cost_enabled(self):
        """Test formatting result message with cost when show_cost=True."""
        config = RendererConfig(show_cost=True)
        formatter = ClaudeCodeFormatter(config)
        message = ResultMessage(
            subtype="ended",
            duration_ms=1000,
            duration_api_ms=500,
            is_error=False,
            num_turns=1,
            session_id="session-123",
            total_cost_usd=0.0042,
        )
        result = formatter.format_result_message(message)
        expected = "\u25cf Result ended\n  Cost: $0.0042"
        assert result == expected

    def test_format_result_message_without_cost(self):
        """Test formatting result message without cost."""
        formatter = ClaudeCodeFormatter()
        message = ResultMessage(
            subtype="ended",
            duration_ms=1000,
            duration_api_ms=500,
            is_error=False,
            num_turns=1,
            session_id="session-123",
            total_cost_usd=None,
        )
        result = formatter.format_result_message(message)
        assert result == "\u25cf Result ended"
        assert "Cost" not in result

    def test_format_stream_event(self):
        """Test formatting stream event."""
        formatter = ClaudeCodeFormatter()
        message = StreamEvent(
            uuid="uuid-123",
            session_id="session-123",
            event={"type": "content_block_start"},
        )
        result = formatter.format_stream_event(message)
        assert "content_block_start" in result

    def test_format_stream_event_unknown_type(self):
        """Test formatting stream event with unknown type."""
        formatter = ClaudeCodeFormatter()
        message = StreamEvent(uuid="uuid-123", session_id="session-123", event={})
        result = formatter.format_stream_event(message)
        assert "unknown" in result

    def test_format_dispatches_to_correct_method(self):
        """Test that format() dispatches to correct type-specific method."""
        formatter = ClaudeCodeFormatter()

        # Test UserMessage
        user_msg = UserMessage(content="Hello")
        result = formatter.format(user_msg)
        assert "User:" in result

        # Test AssistantMessage
        assistant_msg = AssistantMessage(
            content=[TextBlock(text="Hi")], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format(assistant_msg)
        assert "Hi" in result

        # Test SystemMessage
        system_msg = SystemMessage(subtype="test", data={})
        result = formatter.format(system_msg)
        assert "System:" in result

        # Test ResultMessage
        result_msg = ResultMessage(
            subtype="ended",
            duration_ms=1000,
            duration_api_ms=500,
            is_error=False,
            num_turns=1,
            session_id="session-123",
            total_cost_usd=0.01,
        )
        result = formatter.format(result_msg)
        assert "Result ended" in result

        # Test StreamEvent
        stream_msg = StreamEvent(
            uuid="uuid-123", session_id="session-123", event={"type": "test"}
        )
        result = formatter.format(stream_msg)
        assert "Stream:" in result

    def test_truncate_text_no_truncation_needed(self):
        """Test that text shorter than max_length is not truncated."""
        formatter = ClaudeCodeFormatter()
        text = "Short text"
        result = formatter._truncate_text(text, max_length=100)
        assert result == text

    def test_truncate_text_with_truncation(self):
        """Test text truncation with line count indicator."""
        formatter = ClaudeCodeFormatter()
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        result = formatter._truncate_text(text, max_length=10)
        assert len(result) > 10  # Includes indicator
        assert "+4 lines" in result or "+3 lines" in result  # Depends on exact cut

    def test_indent_lines(self):
        """Test line indentation helper."""
        formatter = ClaudeCodeFormatter()
        text = "Line 1\nLine 2"
        result = formatter._indent_lines(text, indent="  ")
        assert result == "  Line 1\n  Line 2"

    def test_indent_lines_custom_indent(self):
        """Test line indentation with custom prefix."""
        formatter = ClaudeCodeFormatter()
        text = "A\nB"
        result = formatter._indent_lines(text, indent=">>> ")
        assert result == ">>> A\n>>> B"


class TestRenderLevelFiltering:
    """Test render level filtering behavior in format_assistant_message."""

    def test_minimal_level_shows_only_text(self):
        """Test MINIMAL level hides tool blocks and shows only text."""
        config = RendererConfig(render_level=RenderLevel.MINIMAL)
        formatter = ClaudeCodeFormatter(config)

        # Create message with text, tool use, and tool result
        message = AssistantMessage(
            content=[
                TextBlock(text="Let me check that for you."),
                ToolUseBlock(id="1", name="Read", input={"file_path": "test.txt"}),
                ToolResultBlock(tool_use_id="1", content="file content"),
                TextBlock(text="Here's what I found."),
            ],
            model="claude-3-5-sonnet-20241022",
        )

        result = formatter.format_assistant_message(message)

        # Should only show text blocks
        assert "Let me check that for you." in result
        assert "Here's what I found." in result
        # Should NOT show tool blocks
        assert "Read" not in result
        assert "file content" not in result

    def test_standard_level_shows_tools_not_results(self):
        """Test STANDARD level shows tool use but hides tool results."""
        config = RendererConfig(render_level=RenderLevel.STANDARD)
        formatter = ClaudeCodeFormatter(config)

        message = AssistantMessage(
            content=[
                TextBlock(text="Checking file."),
                ToolUseBlock(id="1", name="Read", input={"file_path": "test.txt"}),
                ToolResultBlock(tool_use_id="1", content="file content here"),
            ],
            model="claude-3-5-sonnet-20241022",
        )

        result = formatter.format_assistant_message(message)

        # Should show text and tool use
        assert "Checking file." in result
        assert "Read" in result
        # Should NOT show tool result content
        assert "file content here" not in result

    def test_detailed_level_shows_everything(self):
        """Test DETAILED level shows all blocks including tool results."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)

        message = AssistantMessage(
            content=[
                TextBlock(text="Reading file."),
                ToolUseBlock(id="1", name="Read", input={"file_path": "test.txt"}),
                ToolResultBlock(tool_use_id="1", content="file content"),
            ],
            model="claude-3-5-sonnet-20241022",
        )

        result = formatter.format_assistant_message(message)

        # Should show everything
        assert "Reading file." in result
        assert "Read" in result
        assert "file content" in result

    def test_minimal_level_shows_thinking_blocks(self):
        """Test MINIMAL level shows thinking blocks (they're always shown)."""
        config = RendererConfig(render_level=RenderLevel.MINIMAL)
        formatter = ClaudeCodeFormatter(config)

        message = AssistantMessage(
            content=[
                ThinkingBlock(thinking="Let me think about this...", signature="sig-1"),
                ToolUseBlock(id="1", name="Read", input={"file_path": "test.txt"}),
            ],
            model="claude-3-5-sonnet-20241022",
        )

        result = formatter.format_assistant_message(message)

        # Should show thinking
        assert "Let me think about this..." in result
        # Should NOT show tool
        assert "Read" not in result

    def test_render_level_with_multiple_tool_blocks(self):
        """Test render level filtering works with multiple tool blocks."""
        config = RendererConfig(render_level=RenderLevel.STANDARD)
        formatter = ClaudeCodeFormatter(config)

        message = AssistantMessage(
            content=[
                ToolUseBlock(id="1", name="Read", input={"file": "a.txt"}),
                ToolResultBlock(tool_use_id="1", content="content A"),
                ToolUseBlock(id="2", name="Write", input={"file": "b.txt"}),
                ToolResultBlock(tool_use_id="2", content="success"),
            ],
            model="claude-3-5-sonnet-20241022",
        )

        result = formatter.format_assistant_message(message)

        # Should show both tool uses
        assert "Read" in result
        assert "Write" in result
        # Should NOT show any tool results
        assert "content A" not in result
        assert "success" not in result
