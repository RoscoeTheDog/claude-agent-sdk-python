"""Tests for system message severity-based filtering (Story 5)."""

from io import StringIO

from claude_agent_sdk.rendering import (
    ClaudeCodeFormatter,
    RendererConfig,
    RenderLevel,
    StreamHandler,
    SystemMessageLevel,
)
from claude_agent_sdk.types import SystemMessage


class TestSystemMessageLevel:
    """Test SystemMessageLevel enum values and ordering."""

    def test_system_message_level_values(self):
        """Test that SystemMessageLevel has expected values."""
        assert SystemMessageLevel.DEBUG == 0
        assert SystemMessageLevel.INFO == 1
        assert SystemMessageLevel.WARNING == 2
        assert SystemMessageLevel.ERROR == 3
        assert SystemMessageLevel.CRITICAL == 4

    def test_system_message_level_ordering(self):
        """Test that SystemMessageLevel values are properly ordered."""
        assert SystemMessageLevel.DEBUG < SystemMessageLevel.INFO
        assert SystemMessageLevel.INFO < SystemMessageLevel.WARNING
        assert SystemMessageLevel.WARNING < SystemMessageLevel.ERROR
        assert SystemMessageLevel.ERROR < SystemMessageLevel.CRITICAL


class TestSeverityDetection:
    """Test severity detection from system message subtypes."""

    def test_detect_critical_severity(self):
        """Test detection of CRITICAL severity."""
        from claude_agent_sdk.rendering.base import _detect_system_message_severity

        msg = SystemMessage(subtype="critical_error", data={})
        assert _detect_system_message_severity(msg) == SystemMessageLevel.CRITICAL

        msg2 = SystemMessage(subtype="CRITICAL", data={})
        assert _detect_system_message_severity(msg2) == SystemMessageLevel.CRITICAL

    def test_detect_error_severity(self):
        """Test detection of ERROR severity."""
        from claude_agent_sdk.rendering.base import _detect_system_message_severity

        msg = SystemMessage(subtype="error", data={})
        assert _detect_system_message_severity(msg) == SystemMessageLevel.ERROR

        msg2 = SystemMessage(subtype="operation_failed", data={})
        assert _detect_system_message_severity(msg2) == SystemMessageLevel.ERROR

    def test_detect_warning_severity(self):
        """Test detection of WARNING severity."""
        from claude_agent_sdk.rendering.base import _detect_system_message_severity

        msg = SystemMessage(subtype="warning", data={})
        assert _detect_system_message_severity(msg) == SystemMessageLevel.WARNING

        msg2 = SystemMessage(subtype="warn", data={})
        assert _detect_system_message_severity(msg2) == SystemMessageLevel.WARNING

    def test_detect_debug_severity(self):
        """Test detection of DEBUG severity."""
        from claude_agent_sdk.rendering.base import _detect_system_message_severity

        msg = SystemMessage(subtype="debug", data={})
        assert _detect_system_message_severity(msg) == SystemMessageLevel.DEBUG

    def test_detect_info_severity(self):
        """Test detection of INFO severity (default)."""
        from claude_agent_sdk.rendering.base import _detect_system_message_severity

        msg = SystemMessage(subtype="info", data={})
        assert _detect_system_message_severity(msg) == SystemMessageLevel.INFO

        # Unknown subtypes default to INFO
        msg2 = SystemMessage(subtype="unknown", data={})
        assert _detect_system_message_severity(msg2) == SystemMessageLevel.INFO


class TestSystemMessageFiltering:
    """Test system message filtering based on render level and severity."""

    def test_minimal_level_shows_only_critical(self):
        """Test that MINIMAL level shows only CRITICAL messages."""
        config = RendererConfig(render_level=RenderLevel.MINIMAL)
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, config=config, stream=stream)

        # CRITICAL should be shown
        critical_msg = SystemMessage(subtype="critical_error", data={})
        handler.handle(critical_msg)
        assert "System:" in stream.getvalue()

        # ERROR should be hidden
        stream.truncate(0)
        stream.seek(0)
        error_msg = SystemMessage(subtype="error", data={})
        handler.handle(error_msg)
        assert stream.getvalue() == ""

        # WARNING should be hidden
        warning_msg = SystemMessage(subtype="warning", data={})
        handler.handle(warning_msg)
        assert stream.getvalue() == ""

        # INFO should be hidden
        info_msg = SystemMessage(subtype="info", data={})
        handler.handle(info_msg)
        assert stream.getvalue() == ""

    def test_standard_level_shows_error_and_above(self):
        """Test that STANDARD level shows ERROR and above (default config)."""
        config = RendererConfig(render_level=RenderLevel.STANDARD)
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, config=config, stream=stream)

        # CRITICAL should be shown
        critical_msg = SystemMessage(subtype="critical_error", data={})
        handler.handle(critical_msg)
        assert "System:" in stream.getvalue()

        # ERROR should be shown
        stream.truncate(0)
        stream.seek(0)
        error_msg = SystemMessage(subtype="error", data={})
        handler.handle(error_msg)
        assert "System:" in stream.getvalue()

        # WARNING should be hidden (default min_system_message_level is ERROR)
        stream.truncate(0)
        stream.seek(0)
        warning_msg = SystemMessage(subtype="warning", data={})
        handler.handle(warning_msg)
        assert stream.getvalue() == ""

        # INFO should be hidden
        stream.truncate(0)
        stream.seek(0)
        info_msg = SystemMessage(subtype="info", data={})
        handler.handle(info_msg)
        assert stream.getvalue() == ""

    def test_detailed_level_shows_all_messages(self):
        """Test that DETAILED level shows all system messages."""
        config = RendererConfig(render_level=RenderLevel.DETAILED)
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, config=config, stream=stream)

        # All severity levels should be shown
        for subtype in ["critical", "error", "warning", "info", "debug"]:
            stream.truncate(0)
            stream.seek(0)
            msg = SystemMessage(subtype=subtype, data={})
            handler.handle(msg)
            assert "System:" in stream.getvalue(), f"Failed for subtype: {subtype}"

    def test_debug_level_shows_all_messages(self):
        """Test that DEBUG level shows all system messages."""
        config = RendererConfig(render_level=RenderLevel.DEBUG)
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, config=config, stream=stream)

        # All severity levels should be shown
        for subtype in ["critical", "error", "warning", "info", "debug"]:
            stream.truncate(0)
            stream.seek(0)
            msg = SystemMessage(subtype=subtype, data={})
            handler.handle(msg)
            assert "System:" in stream.getvalue(), f"Failed for subtype: {subtype}"

    def test_custom_min_severity_level(self):
        """Test custom min_system_message_level configuration."""
        # Set to show WARNING and above at STANDARD level
        config = RendererConfig(
            render_level=RenderLevel.STANDARD,
            min_system_message_level=SystemMessageLevel.WARNING,
        )
        formatter = ClaudeCodeFormatter(config)
        stream = StringIO()
        handler = StreamHandler(formatter, config=config, stream=stream)

        # WARNING should be shown
        warning_msg = SystemMessage(subtype="warning", data={})
        handler.handle(warning_msg)
        assert "System:" in stream.getvalue()

        # INFO should be hidden
        stream.truncate(0)
        stream.seek(0)
        info_msg = SystemMessage(subtype="info", data={})
        handler.handle(info_msg)
        assert stream.getvalue() == ""

    def test_below_minimal_hides_all_system_messages(self):
        """Test that levels below MINIMAL hide all system messages."""
        # This tests the else clause for levels below MINIMAL (if any exist)
        config = RendererConfig(render_level=RenderLevel.MINIMAL)
        formatter = ClaudeCodeFormatter(config)

        # Manually set render level to -1 (hypothetical level below MINIMAL)
        config.render_level = -1

        stream = StringIO()
        handler = StreamHandler(formatter, config=config, stream=stream)

        # Even CRITICAL should be hidden
        critical_msg = SystemMessage(subtype="critical", data={})
        handler.handle(critical_msg)
        assert stream.getvalue() == ""


class TestRendererConfigDefaults:
    """Test RendererConfig default values for system message filtering."""

    def test_default_min_system_message_level(self):
        """Test that default min_system_message_level is ERROR."""
        config = RendererConfig()
        assert config.min_system_message_level == SystemMessageLevel.ERROR

    def test_config_serialization_with_system_message_level(self):
        """Test that min_system_message_level is properly serialized."""
        config = RendererConfig(min_system_message_level=SystemMessageLevel.WARNING)
        data = config._to_dict()
        assert data["min_system_message_level"] == "WARNING"

    def test_config_deserialization_from_string(self):
        """Test that min_system_message_level can be deserialized from string."""
        data = {"min_system_message_level": "WARNING"}
        config = RendererConfig._from_dict(data)
        assert config.min_system_message_level == SystemMessageLevel.WARNING

    def test_config_deserialization_from_int(self):
        """Test that min_system_message_level can be deserialized from int."""
        data = {"min_system_message_level": 2}  # WARNING = 2
        config = RendererConfig._from_dict(data)
        assert config.min_system_message_level == SystemMessageLevel.WARNING
