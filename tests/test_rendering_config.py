"""Tests for rendering configuration classes."""

import pytest

from claude_agent_sdk.rendering import RendererConfig, RenderLevel


class TestRenderLevel:
    """Test RenderLevel enum."""

    def test_render_level_values(self):
        """Test that RenderLevel has correct values."""
        assert RenderLevel.MINIMAL == 0
        assert RenderLevel.STANDARD == 1
        assert RenderLevel.DETAILED == 2
        assert RenderLevel.DEBUG == 3
        assert RenderLevel.ALL == 4

    def test_render_level_ordering(self):
        """Test that RenderLevel values can be compared."""
        assert RenderLevel.MINIMAL < RenderLevel.STANDARD
        assert RenderLevel.STANDARD < RenderLevel.DETAILED
        assert RenderLevel.DETAILED < RenderLevel.DEBUG
        assert RenderLevel.DEBUG < RenderLevel.ALL

    def test_render_level_comparison(self):
        """Test various comparison operations."""
        level = RenderLevel.STANDARD
        assert level >= RenderLevel.MINIMAL
        assert level <= RenderLevel.DEBUG
        assert level != RenderLevel.ALL
        assert level == RenderLevel.STANDARD


class TestRendererConfig:
    """Test RendererConfig dataclass."""

    def test_default_config(self):
        """Test RendererConfig with default values."""
        config = RendererConfig()
        assert config.render_level == RenderLevel.STANDARD
        assert config.include_message_types == []
        assert config.exclude_message_types == []
        assert config.show_metadata is False
        assert config.show_tool_inputs is True
        assert config.show_tool_outputs is True
        assert config.compact_mode is False
        assert config.max_text_length == 10000
        assert config.max_tool_output_length == 5000

    def test_utf8_character_defaults(self):
        """Test that UTF-8 characters match Claude Code CLI defaults."""
        config = RendererConfig()
        assert config.bullet == "\u25cf"  # ●
        assert config.tree_connector == "\u23bf"  # ⎿
        assert config.arrow == "\u2192"  # →
        assert config.ellipsis == "\u2026"  # …
        assert config.list_bullet == "\u00b7"  # ·

    def test_custom_render_level(self):
        """Test creating config with custom render level."""
        config = RendererConfig(render_level=RenderLevel.DEBUG)
        assert config.render_level == RenderLevel.DEBUG

    def test_custom_display_settings(self):
        """Test creating config with custom display settings."""
        config = RendererConfig(
            show_metadata=True,
            show_tool_inputs=False,
            show_tool_outputs=False,
            compact_mode=True,
        )
        assert config.show_metadata is True
        assert config.show_tool_inputs is False
        assert config.show_tool_outputs is False
        assert config.compact_mode is True

    def test_custom_content_limits(self):
        """Test creating config with custom content limits."""
        config = RendererConfig(max_text_length=5000, max_tool_output_length=2000)
        assert config.max_text_length == 5000
        assert config.max_tool_output_length == 2000

    def test_custom_utf8_characters(self):
        """Test creating config with custom UTF-8 characters."""
        config = RendererConfig(
            bullet="*",
            tree_connector="|",
            arrow="->",
            ellipsis="...",
            list_bullet="-",
        )
        assert config.bullet == "*"
        assert config.tree_connector == "|"
        assert config.arrow == "->"
        assert config.ellipsis == "..."
        assert config.list_bullet == "-"

    def test_custom_include_message_types(self):
        """Test creating config with include message types."""
        config = RendererConfig(include_message_types=["UserMessage", "AssistantMessage"])
        assert config.include_message_types == ["UserMessage", "AssistantMessage"]

    def test_custom_exclude_message_types(self):
        """Test creating config with exclude message types."""
        config = RendererConfig(exclude_message_types=["SystemMessage"])
        assert config.exclude_message_types == ["SystemMessage"]

    def test_negative_max_text_length_raises_error(self):
        """Test that negative max_text_length raises ValueError."""
        with pytest.raises(ValueError, match="max_text_length must be non-negative"):
            RendererConfig(max_text_length=-1)

    def test_negative_max_tool_output_length_raises_error(self):
        """Test that negative max_tool_output_length raises ValueError."""
        with pytest.raises(ValueError, match="max_tool_output_length must be non-negative"):
            RendererConfig(max_tool_output_length=-1)

    def test_zero_content_limits_allowed(self):
        """Test that zero content limits are allowed."""
        config = RendererConfig(max_text_length=0, max_tool_output_length=0)
        assert config.max_text_length == 0
        assert config.max_tool_output_length == 0

    def test_config_is_mutable(self):
        """Test that config fields can be modified after creation."""
        config = RendererConfig()
        config.render_level = RenderLevel.DEBUG
        config.show_metadata = True
        assert config.render_level == RenderLevel.DEBUG
        assert config.show_metadata is True
