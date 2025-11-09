"""Unit tests for semantic role taxonomy and detection.

Tests for Story 4.5: Semantic Role Taxonomy & Detection.
Validates the 10-role taxonomy, pattern-based detection, and configuration.
"""

from claude_agent_sdk.rendering.semantic import (
    PatternBasedDetector,
    RoleDetectionConfig,
    SemanticRole,
)


class TestSemanticRoleEnum:
    """Tests for SemanticRole enum."""

    def test_enum_has_all_10_roles(self):
        """Test SemanticRole enum has exactly 10 roles."""
        assert len(SemanticRole) == 10
        expected_roles = {
            "SYSTEM",
            "USER",
            "ASSISTANT",
            "TOOL",
            "ERROR",
            "WARNING",
            "SUCCESS",
            "INFO",
            "CODE",
            "INTERACTIVE",
        }
        assert {role.name for role in SemanticRole} == expected_roles

    def test_enum_values(self):
        """Test SemanticRole enum values match expected strings."""
        assert SemanticRole.ERROR.value == "error"
        assert SemanticRole.WARNING.value == "warning"
        assert SemanticRole.SUCCESS.value == "success"
        assert SemanticRole.SYSTEM.value == "system"
        assert SemanticRole.TOOL.value == "tool"

    def test_role_descriptions(self):
        """Test each role has a description."""
        for role in SemanticRole:
            desc = role.description
            assert isinstance(desc, str)
            assert len(desc) > 0

        # Validate specific descriptions
        assert SemanticRole.ERROR.description == "Error messages, failures, and exceptions"
        assert SemanticRole.SUCCESS.description == "Success indicators and positive confirmations"

    def test_role_default_icons(self):
        """Test roles have appropriate Unicode icons."""
        assert SemanticRole.ERROR.default_icon == "✗"
        assert SemanticRole.WARNING.default_icon == "⚠️"
        assert SemanticRole.SUCCESS.default_icon == "✓"
        assert SemanticRole.INFO.default_icon == "ℹ️"
        assert SemanticRole.TOOL.default_icon == "⟳"
        assert SemanticRole.INTERACTIVE.default_icon == "⊙"

        # Roles without icons return empty string
        assert SemanticRole.SYSTEM.default_icon == ""
        assert SemanticRole.USER.default_icon == ""

    def test_role_repr(self):
        """Test role representation."""
        assert repr(SemanticRole.ERROR) == "SemanticRole.ERROR"
        assert repr(SemanticRole.WARNING) == "SemanticRole.WARNING"


class TestPatternBasedDetector:
    """Tests for PatternBasedDetector class."""

    def test_default_initialization(self):
        """Test detector initializes with default config."""
        detector = PatternBasedDetector()
        assert detector.config is not None
        assert detector.config.enable_type_detection is True
        assert detector.config.enable_content_patterns is True
        assert detector.config.enable_metadata_hints is True

    def test_custom_config_initialization(self):
        """Test detector initializes with custom config."""
        config = RoleDetectionConfig(
            enable_type_detection=False,
            default_role=SemanticRole.INFO,
        )
        detector = PatternBasedDetector(config=config)
        assert detector.config.enable_type_detection is False
        assert detector.config.default_role == SemanticRole.INFO


class TestTypeBasedDetection:
    """Tests for message type-based role detection."""

    def test_error_type_detection(self):
        """Test detection of error message type."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "error"
                self.content = "Test error"

        assert detector.detect(Message()) == SemanticRole.ERROR

    def test_tool_use_type_detection(self):
        """Test detection of tool_use message type."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "tool_use"
                self.content = "Test tool"

        assert detector.detect(Message()) == SemanticRole.TOOL

    def test_tool_result_type_detection(self):
        """Test detection of tool_result message type."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "tool_result"
                self.content = "Test result"

        assert detector.detect(Message()) == SemanticRole.TOOL

    def test_system_type_detection(self):
        """Test detection of system message type."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "system"
                self.content = "System message"

        assert detector.detect(Message()) == SemanticRole.SYSTEM

    def test_user_type_detection(self):
        """Test detection of user message type."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "user"
                self.content = "User input"

        assert detector.detect(Message()) == SemanticRole.USER


class TestContentPatternDetection:
    """Tests for content pattern-based role detection."""

    def test_warning_pattern_detection(self):
        """Test detection of warning content pattern."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = "⚠️ Warning message"

        assert detector.detect(Message()) == SemanticRole.WARNING

    def test_success_pattern_detection(self):
        """Test detection of success content pattern."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = "✓ Success"

        assert detector.detect(Message()) == SemanticRole.SUCCESS

    def test_error_pattern_detection(self):
        """Test detection of error content pattern."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = "✗ Error occurred"

        assert detector.detect(Message()) == SemanticRole.ERROR

    def test_info_pattern_detection(self):
        """Test detection of info content patterns."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self, content):
                self.type = "assistant"
                self.content = content

        # Test multiple info patterns
        assert detector.detect(Message("ℹ️ Information")) == SemanticRole.INFO
        assert detector.detect(Message("Note: Something")) == SemanticRole.INFO
        assert detector.detect(Message("Info: Details")) == SemanticRole.INFO

    def test_pattern_not_matching_middle_of_content(self):
        """Test patterns only match at start of content."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = "This is a ⚠️ warning in the middle"

        # Should fallback to default (ASSISTANT) since pattern is ^⚠️
        assert detector.detect(Message()) == SemanticRole.ASSISTANT


class TestMetadataHintDetection:
    """Tests for metadata.ui.role hint detection."""

    def test_metadata_hint_overrides_type(self):
        """Test metadata hints override type-based detection."""
        detector = PatternBasedDetector()

        class Metadata:
            def __init__(self):
                self.ui = {"role": "warning"}

        class Message:
            def __init__(self):
                self.type = "error"  # Would normally detect as ERROR
                self.content = "Test"
                self.metadata = Metadata()

        # Metadata should override type detection
        assert detector.detect(Message()) == SemanticRole.WARNING

    def test_metadata_hint_dict_style(self):
        """Test metadata hints work with dict-style access."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = "Test"
                self.metadata = {"ui": {"role": "success"}}

        assert detector.detect(Message()) == SemanticRole.SUCCESS

    def test_invalid_metadata_hint_ignored(self):
        """Test invalid metadata hints are ignored gracefully."""
        detector = PatternBasedDetector()

        class Metadata:
            def __init__(self):
                self.ui = {"role": "invalid_role"}

        class Message:
            def __init__(self):
                self.type = "error"
                self.content = "Test"
                self.metadata = Metadata()

        # Invalid hint should be ignored, falls back to type detection
        assert detector.detect(Message()) == SemanticRole.ERROR


class TestDetectionPriority:
    """Tests for detection priority ordering."""

    def test_metadata_overrides_type(self):
        """Test metadata has highest priority over type."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "error"
                self.content = "Test"
                self.metadata = {"ui": {"role": "info"}}

        assert detector.detect(Message()) == SemanticRole.INFO

    def test_metadata_overrides_content_pattern(self):
        """Test metadata has highest priority over content patterns."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = "⚠️ Warning"
                self.metadata = {"ui": {"role": "success"}}

        assert detector.detect(Message()) == SemanticRole.SUCCESS

    def test_type_overrides_content_pattern(self):
        """Test type has priority over content patterns."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "error"
                self.content = "✓ Success"  # Content suggests success

        # Type should win over content pattern
        assert detector.detect(Message()) == SemanticRole.ERROR


class TestFallbackBehavior:
    """Tests for fallback to default role."""

    def test_default_fallback_for_unknown_message(self):
        """Test fallback to default role for unknown patterns."""
        config = RoleDetectionConfig(default_role=SemanticRole.INFO)
        detector = PatternBasedDetector(config)

        class Message:
            def __init__(self):
                self.type = "unknown"
                self.content = "No patterns match"

        assert detector.detect(Message()) == SemanticRole.INFO

    def test_default_fallback_is_assistant(self):
        """Test default fallback is ASSISTANT role."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "unknown"
                self.content = "Random content"

        assert detector.detect(Message()) == SemanticRole.ASSISTANT


class TestCustomPatterns:
    """Tests for custom pattern configuration."""

    def test_custom_error_pattern(self):
        """Test custom error pattern configuration."""
        config = RoleDetectionConfig(
            custom_patterns={
                "ERROR": r"^FAIL:",
            }
        )
        detector = PatternBasedDetector(config)

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = "FAIL: Test failed"

        assert detector.detect(Message()) == SemanticRole.ERROR

    def test_custom_success_pattern(self):
        """Test custom success pattern configuration."""
        config = RoleDetectionConfig(
            custom_patterns={
                "SUCCESS": r"^PASS:",
            }
        )
        detector = PatternBasedDetector(config)

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = "PASS: Test passed"

        assert detector.detect(Message()) == SemanticRole.SUCCESS

    def test_multiple_custom_patterns(self):
        """Test multiple custom patterns."""
        config = RoleDetectionConfig(
            custom_patterns={
                "ERROR": r"^FAIL:",
                "SUCCESS": r"^PASS:",
                "WARNING": r"^CAUTION:",
            }
        )
        detector = PatternBasedDetector(config)

        class Message:
            def __init__(self, content):
                self.type = "assistant"
                self.content = content

        assert detector.detect(Message("FAIL: Error")) == SemanticRole.ERROR
        assert detector.detect(Message("PASS: Good")) == SemanticRole.SUCCESS
        assert detector.detect(Message("CAUTION: Be careful")) == SemanticRole.WARNING

    def test_invalid_custom_pattern_ignored(self):
        """Test invalid custom patterns are ignored gracefully."""
        config = RoleDetectionConfig(
            custom_patterns={
                "INVALID_ROLE": r"^TEST:",  # Invalid role name
                "ERROR": r"[invalid(regex",  # Invalid regex
            }
        )
        # Should not raise error during initialization
        detector = PatternBasedDetector(config)
        assert detector is not None


class TestConfigurationToggling:
    """Tests for enabling/disabling detection methods."""

    def test_disable_type_detection(self):
        """Test disabling type-based detection."""
        config = RoleDetectionConfig(
            enable_type_detection=False,
            enable_content_patterns=False,
            default_role=SemanticRole.INFO,
        )
        detector = PatternBasedDetector(config)

        class Message:
            def __init__(self):
                self.type = "error"
                self.content = "Test"

        # Type detection disabled, should fallback to default
        assert detector.detect(Message()) == SemanticRole.INFO

    def test_disable_content_patterns(self):
        """Test disabling content pattern detection."""
        config = RoleDetectionConfig(
            enable_type_detection=False,
            enable_content_patterns=False,
            default_role=SemanticRole.SYSTEM,
        )
        detector = PatternBasedDetector(config)

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = "⚠️ Warning"

        # Content patterns disabled, should fallback to default
        assert detector.detect(Message()) == SemanticRole.SYSTEM

    def test_disable_metadata_hints(self):
        """Test disabling metadata hint detection."""
        config = RoleDetectionConfig(
            enable_metadata_hints=False,
        )
        detector = PatternBasedDetector(config)

        class Message:
            def __init__(self):
                self.type = "error"
                self.content = "Test"
                self.metadata = {"ui": {"role": "warning"}}

        # Metadata hints disabled, should use type detection
        assert detector.detect(Message()) == SemanticRole.ERROR


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_message_without_type_attribute(self):
        """Test handling messages without type attribute."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.content = "Test content"

        # Should fallback to content or default
        result = detector.detect(Message())
        assert isinstance(result, SemanticRole)

    def test_message_without_content_attribute(self):
        """Test handling messages without content attribute."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "error"

        # Should still detect based on type
        assert detector.detect(Message()) == SemanticRole.ERROR

    def test_message_with_none_content(self):
        """Test handling messages with None content."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = None

        # Should fallback to default
        assert detector.detect(Message()) == SemanticRole.ASSISTANT

    def test_message_with_empty_content(self):
        """Test handling messages with empty string content."""
        detector = PatternBasedDetector()

        class Message:
            def __init__(self):
                self.type = "assistant"
                self.content = ""

        # Should fallback to default
        assert detector.detect(Message()) == SemanticRole.ASSISTANT
