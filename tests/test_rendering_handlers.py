"""Tests for rendering handlers."""

import sys
import tempfile
from io import StringIO
from pathlib import Path

from claude_agent_sdk.rendering import (
    ClaudeCodeFormatter,
    FileHandler,
    MessageRenderer,
    NullHandler,
    RendererConfig,
    RenderLevel,
    StreamHandler,
)
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    UserMessage,
)


class TestStreamHandler:
    """Test StreamHandler."""

    def test_stream_handler_default_stdout(self):
        """Test that StreamHandler defaults to stdout."""
        formatter = ClaudeCodeFormatter()
        handler = StreamHandler(formatter)
        assert handler.stream == sys.stdout

    def test_stream_handler_custom_stream(self):
        """Test StreamHandler with custom stream."""
        formatter = ClaudeCodeFormatter()
        custom_stream = StringIO()
        handler = StreamHandler(formatter, stream=custom_stream)
        assert handler.stream == custom_stream

    def test_stream_handler_writes_to_stream(self):
        """Test that StreamHandler writes formatted output to stream."""
        formatter = ClaudeCodeFormatter()
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)

        message = UserMessage(content="Hello!")
        handler.handle(message)

        output = stream.getvalue()
        assert "\u25cf User: Hello!" in output
        assert output.endswith("\n\n")  # Double newline

    def test_stream_handler_double_newline_separator(self):
        """Test that messages are separated by double newlines."""
        formatter = ClaudeCodeFormatter()
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)

        message1 = UserMessage(content="First")
        message2 = UserMessage(content="Second")
        handler.handle(message1)
        handler.handle(message2)

        output = stream.getvalue()
        # Should have: "First", "", "Second", "", ""
        assert "First" in output
        assert "Second" in output
        assert "\n\n" in output

    def test_stream_handler_auto_flush(self):
        """Test StreamHandler with auto_flush enabled."""
        formatter = ClaudeCodeFormatter()
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream, auto_flush=True)
        assert handler.auto_flush is True

        message = UserMessage(content="Test")
        handler.handle(message)
        # Note: StringIO doesn't actually need flushing, but we verify the flag

    def test_stream_handler_stderr(self):
        """Test StreamHandler writing to stderr."""
        formatter = ClaudeCodeFormatter()
        handler = StreamHandler(formatter, stream=sys.stderr)
        assert handler.stream == sys.stderr


class TestFileHandler:
    """Test FileHandler."""

    def test_file_handler_creates_file(self):
        """Test that FileHandler creates output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "output.txt"
            formatter = ClaudeCodeFormatter()
            handler = FileHandler(formatter, filepath)

            message = UserMessage(content="Hello!")
            handler.handle(message)
            handler.close()

            assert filepath.exists()
            content = filepath.read_text(encoding="utf-8")
            assert "\u25cf User: Hello!" in content

    def test_file_handler_creates_parent_directories(self):
        """Test that FileHandler creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "subdir" / "nested" / "output.txt"
            formatter = ClaudeCodeFormatter()
            handler = FileHandler(formatter, filepath)

            message = UserMessage(content="Test")
            handler.handle(message)
            handler.close()

            assert filepath.exists()
            assert filepath.parent.exists()

    def test_file_handler_append_mode(self):
        """Test FileHandler in append mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "output.txt"
            formatter = ClaudeCodeFormatter()

            # Write first message
            handler1 = FileHandler(formatter, filepath, mode="a")
            message1 = UserMessage(content="First")
            handler1.handle(message1)
            handler1.close()

            # Write second message (should append)
            handler2 = FileHandler(formatter, filepath, mode="a")
            message2 = UserMessage(content="Second")
            handler2.handle(message2)
            handler2.close()

            content = filepath.read_text(encoding="utf-8")
            assert "First" in content
            assert "Second" in content

    def test_file_handler_overwrite_mode(self):
        """Test FileHandler in overwrite mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "output.txt"
            formatter = ClaudeCodeFormatter()

            # Write first message
            handler1 = FileHandler(formatter, filepath, mode="w")
            message1 = UserMessage(content="First")
            handler1.handle(message1)
            handler1.close()

            # Write second message (should overwrite)
            handler2 = FileHandler(formatter, filepath, mode="w")
            message2 = UserMessage(content="Second")
            handler2.handle(message2)
            handler2.close()

            content = filepath.read_text(encoding="utf-8")
            assert "First" not in content
            assert "Second" in content

    def test_file_handler_utf8_encoding(self):
        """Test that FileHandler uses UTF-8 encoding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "output.txt"
            formatter = ClaudeCodeFormatter()
            handler = FileHandler(formatter, filepath)

            # Message with UTF-8 characters
            message = UserMessage(content="Hello \u2022 World \u2192")
            handler.handle(message)
            handler.close()

            content = filepath.read_text(encoding="utf-8")
            assert "\u2022" in content
            assert "\u2192" in content

    def test_file_handler_accepts_string_path(self):
        """Test that FileHandler accepts string paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath_str = str(Path(tmpdir) / "output.txt")
            formatter = ClaudeCodeFormatter()
            handler = FileHandler(formatter, filepath_str)

            message = UserMessage(content="Test")
            handler.handle(message)
            handler.close()

            assert Path(filepath_str).exists()

    def test_file_handler_close_method(self):
        """Test FileHandler close method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "output.txt"
            formatter = ClaudeCodeFormatter()
            handler = FileHandler(formatter, filepath)

            message = UserMessage(content="Test")
            handler.handle(message)

            # Close explicitly
            handler.close()
            assert handler._file_handle is not None
            assert handler._file_handle.closed


class TestNullHandler:
    """Test NullHandler."""

    def test_null_handler_discards_output(self):
        """Test that NullHandler discards all output."""
        formatter = ClaudeCodeFormatter()
        handler = NullHandler(formatter)

        # These should not raise any errors and should produce no output
        message1 = UserMessage(content="Test")
        message2 = AssistantMessage(
            content=[TextBlock(text="Response")], model="claude-3-5-sonnet-20241022"
        )

        handler.handle(message1)
        handler.handle(message2)
        # If we get here without errors, the test passes


class TestHandlerFiltering:
    """Test handler filtering logic."""

    def test_handler_respects_include_list(self):
        """Test that handler respects include_message_types."""
        config = RendererConfig(include_message_types=["UserMessage"])
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, config=config, stream=stream)

        # UserMessage should be rendered
        user_msg = UserMessage(content="Hello")
        handler.handle(user_msg)

        # AssistantMessage should NOT be rendered
        assistant_msg = AssistantMessage(
            content=[TextBlock(text="Hi")], model="claude-3-5-sonnet-20241022"
        )
        handler.handle(assistant_msg)

        output = stream.getvalue()
        assert "Hello" in output
        assert "Hi" not in output

    def test_handler_respects_exclude_list(self):
        """Test that handler respects exclude_message_types."""
        config = RendererConfig(exclude_message_types=["SystemMessage"])
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, config=config, stream=stream)

        # UserMessage should be rendered
        user_msg = UserMessage(content="Hello")
        handler.handle(user_msg)

        # SystemMessage should NOT be rendered
        system_msg = SystemMessage(subtype="test", data={})
        handler.handle(system_msg)

        output = stream.getvalue()
        assert "Hello" in output
        assert "System:" not in output

    def test_handler_filters_system_messages_below_debug_level(self):
        """Test that SystemMessage is filtered at levels below DEBUG."""
        # Standard level (should filter)
        config = RendererConfig(render_level=RenderLevel.STANDARD)
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, config=config, stream=stream)

        system_msg = SystemMessage(subtype="test", data={})
        handler.handle(system_msg)

        assert stream.getvalue() == ""  # No output

        # DEBUG level (should render)
        config_debug = RendererConfig(render_level=RenderLevel.DEBUG)
        formatter_debug = ClaudeCodeFormatter(config_debug)
        stream_debug = StringIO()
        handler_debug = StreamHandler(
            formatter_debug, config=config_debug, stream=stream_debug
        )

        handler_debug.handle(system_msg)
        assert "System:" in stream_debug.getvalue()


class TestMessageRenderer:
    """Test MessageRenderer handler management."""

    def test_message_renderer_add_handler(self):
        """Test adding handlers to renderer."""
        renderer = MessageRenderer()
        formatter = ClaudeCodeFormatter()
        handler = NullHandler(formatter)

        renderer.add_handler(handler)
        assert handler in renderer._handlers

    def test_message_renderer_remove_handler(self):
        """Test removing handlers from renderer."""
        renderer = MessageRenderer()
        formatter = ClaudeCodeFormatter()
        handler = NullHandler(formatter)

        renderer.add_handler(handler)
        renderer.remove_handler(handler)
        assert handler not in renderer._handlers

    def test_message_renderer_clear_handlers(self):
        """Test clearing all handlers."""
        renderer = MessageRenderer()
        formatter = ClaudeCodeFormatter()
        handler1 = NullHandler(formatter)
        handler2 = NullHandler(formatter)

        renderer.add_handler(handler1)
        renderer.add_handler(handler2)
        renderer.clear_handlers()

        assert len(renderer._handlers) == 0

    def test_message_renderer_duplicate_handler(self):
        """Test that adding same handler twice doesn't duplicate it."""
        renderer = MessageRenderer()
        formatter = ClaudeCodeFormatter()
        handler = NullHandler(formatter)

        renderer.add_handler(handler)
        renderer.add_handler(handler)  # Add again

        assert len(renderer._handlers) == 1

    def test_message_renderer_renders_to_all_handlers(self):
        """Test that renderer dispatches to all handlers."""
        renderer = MessageRenderer()
        formatter = ClaudeCodeFormatter()

        stream1 = StringIO()
        stream2 = StringIO()
        handler1 = StreamHandler(formatter, stream=stream1)
        handler2 = StreamHandler(formatter, stream=stream2)

        renderer.add_handler(handler1)
        renderer.add_handler(handler2)

        message = UserMessage(content="Test")
        renderer.render(message)

        assert "Test" in stream1.getvalue()
        assert "Test" in stream2.getvalue()

    def test_message_renderer_handles_handler_errors(self):
        """Test that error in one handler doesn't stop others."""

        class ErrorHandler(StreamHandler):
            def emit(self, formatted_output: str, message) -> None:
                raise RuntimeError("Test error")

        renderer = MessageRenderer()
        formatter = ClaudeCodeFormatter()

        error_handler = ErrorHandler(formatter)
        good_stream = StringIO()
        good_handler = StreamHandler(formatter, stream=good_stream)

        renderer.add_handler(error_handler)
        renderer.add_handler(good_handler)

        message = UserMessage(content="Test")
        # Should not raise, error should be caught
        renderer.render(message)

        # Good handler should still work
        assert "Test" in good_stream.getvalue()

    def test_message_renderer_multiple_messages(self):
        """Test rendering multiple messages."""
        renderer = MessageRenderer()
        formatter = ClaudeCodeFormatter()
        stream = StringIO()
        handler = StreamHandler(formatter, stream=stream)

        renderer.add_handler(handler)

        msg1 = UserMessage(content="First")
        msg2 = AssistantMessage(
            content=[TextBlock(text="Second")], model="claude-3-5-sonnet-20241022"
        )
        msg3 = ResultMessage(
            subtype="ended",
            duration_ms=1000,
            duration_api_ms=500,
            is_error=False,
            num_turns=1,
            session_id="session-123",
            total_cost_usd=0.01,
        )

        renderer.render(msg1)
        renderer.render(msg2)
        renderer.render(msg3)

        output = stream.getvalue()
        assert "First" in output
        assert "Second" in output
        assert "Result ended" in output
