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

    def test_format_tool_result_strips_line_numbers(self):
        """Test that line numbers are stripped for clean display (matching Claude Code CLI)."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)

        # Simulate CLI output with line numbers
        # Input: "     1→# Header" (whitespace + line number + content)
        # Expected: "  ⎿  # Header" (clean display, no line numbers)
        content_with_line_numbers = "     1→# Header\n     2→Content\n     3→More"

        result_block = ToolResultBlock(
            tool_use_id="tool-123", content=content_with_line_numbers
        )
        message = AssistantMessage(
            content=[result_block], model="claude-3-5-sonnet-20241022"
        )
        result = formatter.format_assistant_message(message)

        # Line numbers should be completely removed for clean display
        assert "  \u23bf  # Header" in result
        assert "     Content" in result
        assert "     More" in result

        # Should NOT contain line numbers
        assert "1→" not in result
        assert "2→" not in result
        assert "3→" not in result

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
        """Test that indentation after line numbers (→) is preserved when line numbers are stripped."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)

        # CLI output format: "     1→# Header" and "     7→   - List item"
        # The spaces AFTER → are meaningful indentation that must be preserved
        # After stripping line numbers: "# Header" and "   - List item"
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

        # Line numbers should be stripped, but indentation preserved
        assert "   - **[Pretty Printer Demos]**" in result  # 3 spaces preserved
        assert "      - More indented item" in result  # 6 spaces preserved

        # Should NOT contain line numbers
        assert "7→" not in result
        assert "8→" not in result

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


class TestComponentLevelToolStyling:
    """Test component-level styling for tool calls (Story 3)."""

    def test_format_tool_use_with_active_state(self):
        """Test tool use formatting with active (green bullet) state."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="read_file",
            input={"path": "/path/to/file.py", "lines": 100}
        )

        result = formatter._format_tool_use(tool_block, state="active")

        # Should contain tool name and parameters
        assert "read_file" in result
        assert "path:" in result
        assert "/path/to/file.py" in result
        assert "lines:" in result
        assert "100" in result
        # Bullet should be present
        assert "●" in result

    def test_format_tool_use_with_pending_state(self):
        """Test tool use formatting with pending (white bullet) state."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="search_files",
            input={"query": "test"}
        )

        result = formatter._format_tool_use(tool_block, state="pending")

        # Should contain tool name and parameters
        assert "search_files" in result
        assert "query:" in result
        assert "test" in result

    def test_format_tool_use_with_failed_state(self):
        """Test tool use formatting with failed (red bullet) state."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="delete_file",
            input={"path": "/nonexistent.txt"}
        )

        result = formatter._format_tool_use(tool_block, state="failed")

        # Should contain tool name and parameters
        assert "delete_file" in result
        assert "path:" in result

    def test_format_tool_use_default_state(self):
        """Test tool use formatting defaults to 'active' state."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="test_tool",
            input={}
        )

        # Should default to active when no state provided
        result = formatter._format_tool_use(tool_block)

        assert "test_tool" in result

    def test_format_tool_use_with_string_parameter(self):
        """Test string parameters are styled (green) and quoted."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="echo",
            input={"message": "Hello World"}
        )

        result = formatter._format_tool_use(tool_block)

        # String should be quoted
        assert '"Hello World"' in result

    def test_format_tool_use_with_boolean_parameter(self):
        """Test boolean parameters are styled (cyan)."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="configure",
            input={"enabled": True, "debug": False}
        )

        result = formatter._format_tool_use(tool_block)

        # Booleans should be lowercase
        assert "true" in result
        assert "false" in result

    def test_format_tool_use_with_numeric_parameter(self):
        """Test numeric parameters are styled (green)."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="calculate",
            input={"count": 42, "rate": 3.14}
        )

        result = formatter._format_tool_use(tool_block)

        assert "42" in result
        assert "3.14" in result

    def test_format_tool_use_with_null_parameter(self):
        """Test null parameters are styled (cyan)."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="test",
            input={"value": None}
        )

        result = formatter._format_tool_use(tool_block)

        assert "null" in result

    def test_format_tool_use_with_complex_parameter(self):
        """Test complex types (list, dict) are JSON-formatted."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="configure",
            input={
                "settings": {"key": "value"},
                "items": [1, 2, 3]
            }
        )

        result = formatter._format_tool_use(tool_block)

        # Complex types should be JSON-encoded
        assert "settings:" in result
        assert "items:" in result

    def test_format_tool_use_with_mixed_parameters(self):
        """Test tool with multiple parameter types."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="multi_param",
            input={
                "text": "hello",
                "count": 5,
                "enabled": True,
                "value": None
            }
        )

        result = formatter._format_tool_use(tool_block)

        assert "text:" in result
        assert '"hello"' in result
        assert "count:" in result
        assert "5" in result
        assert "enabled:" in result
        assert "true" in result
        assert "value:" in result
        assert "null" in result

    def test_format_tool_use_with_no_parameters(self):
        """Test tool with empty parameter dict."""
        formatter = ClaudeCodeFormatter()
        tool_block = ToolUseBlock(
            id="tool_1",
            name="list_files",
            input={}
        )

        result = formatter._format_tool_use(tool_block)

        # Should show tool with empty parentheses
        assert "list_files" in result
        assert "()" in result


class TestLargeResponseWarning:
    """Test warning indicators for large MCP responses (Story 3)."""

    def test_estimate_token_count_empty_content(self):
        """Test token estimation for empty/None content."""
        formatter = ClaudeCodeFormatter()

        assert formatter._estimate_token_count(None) == 0
        assert formatter._estimate_token_count("") == 0

    def test_estimate_token_count_string_content(self):
        """Test token estimation for string content."""
        formatter = ClaudeCodeFormatter()

        # "hello" = 5 chars / 4 = 1 token (rough estimate)
        assert formatter._estimate_token_count("hello") == 1

        # 400 chars = 100 tokens
        content = "x" * 400
        assert formatter._estimate_token_count(content) == 100

    def test_estimate_token_count_complex_content(self):
        """Test token estimation for dict/list content."""
        formatter = ClaudeCodeFormatter()

        content = {"key": "value", "items": [1, 2, 3]}
        # JSON representation will be estimated
        tokens = formatter._estimate_token_count(content)
        assert tokens > 0

    def test_format_tool_result_warning_small_response(self):
        """Test no warning for small responses (<10k tokens)."""
        formatter = ClaudeCodeFormatter()

        # 5000 tokens - should not trigger warning
        warning = formatter._format_tool_result_warning(5000)
        assert warning == ""

        # 9999 tokens - should not trigger warning
        warning = formatter._format_tool_result_warning(9999)
        assert warning == ""

    def test_format_tool_result_warning_large_response(self):
        """Test warning generated for large responses (>10k tokens)."""
        formatter = ClaudeCodeFormatter()

        # 10001 tokens - should trigger warning
        warning = formatter._format_tool_result_warning(10001)
        assert warning != ""
        assert "⚠️" in warning
        assert "Large MCP response" in warning
        assert "10.0k tokens" in warning

        # 15000 tokens
        warning = formatter._format_tool_result_warning(15000)
        assert "15.0k tokens" in warning

    def test_format_tool_result_warning_very_large_response(self):
        """Test warning formatting for very large responses."""
        formatter = ClaudeCodeFormatter()

        # 100k tokens
        warning = formatter._format_tool_result_warning(100000)
        assert "100.0k tokens" in warning
        assert "context quickly" in warning

    def test_format_tool_result_content_with_warning(self):
        """Test tool result formatting includes warning for large content."""
        formatter = ClaudeCodeFormatter()

        # Create large content (>10k tokens = >40k chars)
        large_content = "x" * 50000  # 12.5k tokens
        tool_block = ToolResultBlock(
            tool_use_id="tool_1",
            content=large_content,
            is_error=False
        )

        result = formatter._format_tool_result_content(tool_block)

        # Should include warning
        assert "⚠️" in result
        assert "Large MCP response" in result

    def test_format_tool_result_content_without_warning(self):
        """Test tool result formatting has no warning for small content."""
        formatter = ClaudeCodeFormatter()

        # Create small content
        small_content = "Success"
        tool_block = ToolResultBlock(
            tool_use_id="tool_1",
            content=small_content,
            is_error=False
        )

        result = formatter._format_tool_result_content(tool_block)

        # Should NOT include warning
        assert "⚠️" not in result
        assert "Large MCP response" not in result


class TestBulletListIndentation:
    """Test bullet list indentation fixes (Story 6)."""

    def test_simple_bullet_list_indentation(self):
        """Test that bullet lists are indented from the initial bullet position."""
        formatter = ClaudeCodeFormatter()
        text = "I've created a function with:\n- Input validation\n- Efficient algorithm"
        message = AssistantMessage(
            content=[TextBlock(text=text)],
            model="claude-3-5-sonnet-20241022"
        )

        result = formatter.format_assistant_message(message)

        # First line should have bullet
        assert result.startswith("● I've created a function with:")
        # Subsequent lines should be indented with 2 spaces (bullet position)
        assert "\n  - Input validation" in result
        assert "\n  - Efficient algorithm" in result

    def test_nested_bullet_list_indentation(self):
        """Test that nested bullet lists preserve their indentation."""
        formatter = ClaudeCodeFormatter()
        text = "Features:\n- Authentication\n  - OAuth support\n  - API key auth\n- Database\n  - PostgreSQL\n  - SQLite"
        message = AssistantMessage(
            content=[TextBlock(text=text)],
            model="claude-3-5-sonnet-20241022"
        )

        result = formatter.format_assistant_message(message)

        # Top-level items indented from bullet
        assert "\n  - Authentication" in result
        assert "\n  - Database" in result
        # Nested items should preserve their extra indentation
        assert "\n    - OAuth support" in result
        assert "\n    - API key auth" in result
        assert "\n    - PostgreSQL" in result
        assert "\n    - SQLite" in result

    def test_numbered_list_indentation(self):
        """Test that numbered lists are properly indented."""
        formatter = ClaudeCodeFormatter()
        text = "Steps to follow:\n1. Clone the repository\n2. Install dependencies\n3. Run tests"
        message = AssistantMessage(
            content=[TextBlock(text=text)],
            model="claude-3-5-sonnet-20241022"
        )

        result = formatter.format_assistant_message(message)

        assert "\n  1. Clone the repository" in result
        assert "\n  2. Install dependencies" in result
        assert "\n  3. Run tests" in result

    def test_multiline_list_item_hanging_indent(self):
        """Test that multi-line list items have hanging indent."""
        formatter = ClaudeCodeFormatter()
        text = "Changes made:\n- Updated the authentication module\n  to support OAuth2 flow\n- Fixed validation logic"
        message = AssistantMessage(
            content=[TextBlock(text=text)],
            model="claude-3-5-sonnet-20241022"
        )

        result = formatter.format_assistant_message(message)

        # First list item
        assert "\n  - Updated the authentication module" in result
        # Continuation of first item should be indented further
        assert "\n    to support OAuth2 flow" in result
        # Second list item
        assert "\n  - Fixed validation logic" in result

    def test_mixed_list_types(self):
        """Test handling of mixed list marker types."""
        formatter = ClaudeCodeFormatter()
        text = "Tasks:\n- First task\n* Second task\n+ Third task\n1. Numbered task"
        message = AssistantMessage(
            content=[TextBlock(text=text)],
            model="claude-3-5-sonnet-20241022"
        )

        result = formatter.format_assistant_message(message)

        # All should be indented
        assert "\n  - First task" in result
        assert "\n  * Second task" in result
        assert "\n  + Third task" in result
        assert "\n  1. Numbered task" in result

    def test_plain_multiline_text_hanging_indent(self):
        """Test that plain multi-line text (no bullets) has hanging indent."""
        formatter = ClaudeCodeFormatter()
        text = "This is a long message that spans\nmultiple lines without\nany bullet points"
        message = AssistantMessage(
            content=[TextBlock(text=text)],
            model="claude-3-5-sonnet-20241022"
        )

        result = formatter.format_assistant_message(message)

        # First line has bullet
        assert result.startswith("● This is a long message that spans")
        # Continuation lines should be indented
        assert "\n  multiple lines without" in result
        assert "\n  any bullet points" in result

    def test_empty_lines_preserved(self):
        """Test that empty lines within text are preserved."""
        formatter = ClaudeCodeFormatter()
        text = "First paragraph\n\nSecond paragraph\n- List item"
        message = AssistantMessage(
            content=[TextBlock(text=text)],
            model="claude-3-5-sonnet-20241022"
        )

        result = formatter.format_assistant_message(message)

        # Should have empty line between paragraphs
        assert "First paragraph\n\n" in result
        assert "\n  Second paragraph" in result
        assert "\n  - List item" in result

    def test_thinking_block_indentation(self):
        """Test that thinking blocks also get proper indentation."""
        formatter = ClaudeCodeFormatter()
        thinking = "I need to:\n- Analyze the code\n- Find the bug\n- Fix it"
        message = AssistantMessage(
            content=[ThinkingBlock(thinking=thinking, signature="sig-123")],
            model="claude-3-5-sonnet-20241022"
        )

        result = formatter.format_assistant_message(message)

        # Thinking blocks should also have indented lists
        assert result.startswith("● I need to:")
        assert "\n  - Analyze the code" in result
        assert "\n  - Find the bug" in result
        assert "\n  - Fix it" in result

    def test_single_line_text_unchanged(self):
        """Test that single-line text works as before."""
        formatter = ClaudeCodeFormatter()
        text = "Hello, how can I help you?"
        message = AssistantMessage(
            content=[TextBlock(text=text)],
            model="claude-3-5-sonnet-20241022"
        )

        result = formatter.format_assistant_message(message)

        # Should just be bullet + text (no indentation needed)
        assert result == "● Hello, how can I help you?"

    def test_code_block_preservation(self):
        """Test that code-like content is handled correctly."""
        formatter = ClaudeCodeFormatter()
        text = "Here's the code:\n    def hello():\n        print('hi')"
        message = AssistantMessage(
            content=[TextBlock(text=text)],
            model="claude-3-5-sonnet-20241022"
        )

        result = formatter.format_assistant_message(message)

        # First line
        assert result.startswith("● Here's the code:")
        # Indented code lines should preserve their indentation relative to base
        assert "\n      def hello():" in result
        assert "\n          print('hi')" in result
