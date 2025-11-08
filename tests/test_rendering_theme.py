"""Tests for the theme system."""

import pytest

from claude_agent_sdk.rendering.theme import ColorDepth, StyleRule, Theme


class TestColorDepth:
    """Tests for ColorDepth enum."""

    def test_color_depth_values(self):
        """Test that ColorDepth enum has correct values."""
        assert ColorDepth.NONE == 0
        assert ColorDepth.BASIC_16 == 16
        assert ColorDepth.EXTENDED_256 == 256
        assert ColorDepth.TRUECOLOR == 16777216

    def test_color_depth_ordering(self):
        """Test that ColorDepth values are properly ordered."""
        assert ColorDepth.NONE < ColorDepth.BASIC_16
        assert ColorDepth.BASIC_16 < ColorDepth.EXTENDED_256
        assert ColorDepth.EXTENDED_256 < ColorDepth.TRUECOLOR


class TestStyleRule:
    """Tests for StyleRule dataclass."""

    def test_default_style_rule(self):
        """Test StyleRule with default values."""
        rule = StyleRule()
        assert rule.fg_color is None
        assert rule.bg_color is None
        assert rule.bold is False
        assert rule.dim is False
        assert rule.italic is False
        assert rule.underline is False

    def test_style_rule_with_named_color(self):
        """Test StyleRule with named color."""
        rule = StyleRule(fg_color="red", bold=True)
        assert rule.fg_color == "red"
        assert rule.bold is True

    def test_style_rule_with_rgb_color(self):
        """Test StyleRule with RGB color tuple."""
        rule = StyleRule(fg_color=(255, 0, 0), bg_color=(0, 0, 0))
        assert rule.fg_color == (255, 0, 0)
        assert rule.bg_color == (0, 0, 0)

    def test_style_rule_with_256_color_index(self):
        """Test StyleRule with 256-color index."""
        rule = StyleRule(fg_color=196)  # Bright red in 256-color
        assert rule.fg_color == 196

    def test_style_rule_with_all_attributes(self):
        """Test StyleRule with all attributes set."""
        rule = StyleRule(
            fg_color="blue",
            bg_color="white",
            bold=True,
            dim=False,
            italic=True,
            underline=True,
        )
        assert rule.fg_color == "blue"
        assert rule.bg_color == "white"
        assert rule.bold is True
        assert rule.dim is False
        assert rule.italic is True
        assert rule.underline is True


class TestTheme:
    """Tests for Theme dataclass."""

    def test_default_theme(self):
        """Test Theme with default values."""
        theme = Theme()
        # Verify all categories exist with default StyleRule
        assert isinstance(theme.user_message, StyleRule)
        assert isinstance(theme.assistant_message, StyleRule)
        assert isinstance(theme.system_message, StyleRule)
        assert isinstance(theme.tool_use, StyleRule)
        assert isinstance(theme.tool_result, StyleRule)
        assert isinstance(theme.tool_error, StyleRule)
        assert isinstance(theme.error, StyleRule)
        assert isinstance(theme.warning, StyleRule)
        assert isinstance(theme.success, StyleRule)
        assert isinstance(theme.info, StyleRule)
        assert isinstance(theme.debug, StyleRule)
        assert isinstance(theme.bullet, StyleRule)
        assert isinstance(theme.tree_connector, StyleRule)
        assert isinstance(theme.metadata, StyleRule)
        assert isinstance(theme.truncation, StyleRule)
        assert isinstance(theme.code_block, StyleRule)
        assert isinstance(theme.inline_code, StyleRule)
        assert isinstance(theme.thinking, StyleRule)
        assert isinstance(theme.cost_display, StyleRule)

    def test_claude_code_default_preset(self):
        """Test the claude_code_default preset theme."""
        theme = Theme.claude_code_default()

        # Verify message types
        assert theme.user_message.fg_color == "bright_white"
        assert theme.user_message.bold is True
        assert theme.assistant_message.fg_color == "white"
        assert theme.system_message.fg_color == "bright_black"
        assert theme.system_message.dim is True

        # Verify tool-related
        assert theme.tool_use.fg_color == "bright_blue"
        assert theme.tool_use.bold is True
        assert theme.tool_result.fg_color == "blue"
        assert theme.tool_error.fg_color == "bright_red"
        assert theme.tool_error.bold is True

        # Verify semantic categories
        assert theme.error.fg_color == "bright_red"
        assert theme.error.bold is True
        assert theme.warning.fg_color == "bright_yellow"
        assert theme.warning.bold is True
        assert theme.success.fg_color == "bright_green"
        assert theme.success.bold is True
        assert theme.info.fg_color == "bright_cyan"
        assert theme.debug.fg_color == "bright_black"
        assert theme.debug.dim is True

        # Verify UI elements
        assert theme.bullet.fg_color == "bright_black"
        assert theme.bullet.dim is True
        assert theme.tree_connector.fg_color == "bright_black"
        assert theme.tree_connector.dim is True
        assert theme.metadata.fg_color == "bright_black"
        assert theme.metadata.dim is True
        assert theme.truncation.fg_color == "bright_black"
        assert theme.truncation.dim is True
        assert theme.truncation.italic is True

        # Verify code elements
        assert theme.code_block.fg_color == "cyan"
        assert theme.inline_code.fg_color == "bright_cyan"

        # Verify special
        assert theme.thinking.fg_color == "magenta"
        assert theme.thinking.italic is True
        assert theme.cost_display.fg_color == "bright_black"
        assert theme.cost_display.dim is True

    def test_from_preset_valid_names(self):
        """Test loading themes from valid preset names."""
        # Test canonical name
        theme1 = Theme.from_preset("claude_code")
        assert theme1.error.fg_color == "bright_red"

        # Test alternative name
        theme2 = Theme.from_preset("claude_code_default")
        assert theme2.error.fg_color == "bright_red"

        # Test case insensitivity
        theme3 = Theme.from_preset("CLAUDE_CODE")
        assert theme3.error.fg_color == "bright_red"

    def test_from_preset_invalid_name(self):
        """Test that from_preset raises ValueError for invalid names."""
        with pytest.raises(ValueError) as exc_info:
            Theme.from_preset("nonexistent_theme")

        assert "Unknown theme preset" in str(exc_info.value)
        assert "nonexistent_theme" in str(exc_info.value)
        assert "Available:" in str(exc_info.value)

    def test_to_dict_serialization(self):
        """Test serializing a theme to dictionary."""
        theme = Theme(
            error=StyleRule(fg_color="red", bold=True),
            success=StyleRule(fg_color="green"),
        )
        data = theme.to_dict()

        # Verify structure
        assert isinstance(data, dict)
        assert "error" in data
        assert "success" in data

        # Verify error category
        assert data["error"]["fg_color"] == "red"
        assert data["error"]["bold"] is True
        assert data["error"]["bg_color"] is None

        # Verify success category
        assert data["success"]["fg_color"] == "green"
        assert data["success"]["bold"] is False

    def test_from_dict_deserialization(self):
        """Test deserializing a theme from dictionary."""
        data = {
            "error": {"fg_color": "red", "bold": True},
            "success": {"fg_color": "green", "bold": False},
        }
        theme = Theme.from_dict(data)

        # Verify deserialized values
        assert isinstance(theme.error, StyleRule)
        assert theme.error.fg_color == "red"
        assert theme.error.bold is True

        assert isinstance(theme.success, StyleRule)
        assert theme.success.fg_color == "green"
        assert theme.success.bold is False

    def test_round_trip_serialization(self):
        """Test that serialization and deserialization are reversible."""
        original = Theme.claude_code_default()
        data = original.to_dict()
        restored = Theme.from_dict(data)

        # Compare key attributes
        assert restored.error.fg_color == original.error.fg_color
        assert restored.error.bold == original.error.bold
        assert restored.success.fg_color == original.success.fg_color
        assert restored.tool_use.fg_color == original.tool_use.fg_color
        assert restored.tool_use.bold == original.tool_use.bold

    def test_from_dict_with_rgb_colors(self):
        """Test deserializing theme with RGB color tuples."""
        data = {
            "error": {"fg_color": [255, 0, 0], "bold": True},
            "success": {"fg_color": [0, 255, 0]},
        }
        # Note: JSON doesn't have tuples, so lists are used
        # We need to handle this in from_dict if we want to support JSON loading
        # For now, this test documents the current behavior
        theme = Theme.from_dict(data)

        assert theme.error.fg_color == [255, 0, 0]  # List, not tuple
        assert theme.success.fg_color == [0, 255, 0]

    def test_from_dict_with_256_color_indices(self):
        """Test deserializing theme with 256-color indices."""
        data = {
            "error": {"fg_color": 196, "bold": True},  # Bright red
            "success": {"fg_color": 46},  # Bright green
        }
        theme = Theme.from_dict(data)

        assert theme.error.fg_color == 196
        assert theme.success.fg_color == 46

    def test_from_dict_invalid_value_type(self):
        """Test that from_dict raises ValueError for invalid value types."""
        data = {
            "error": "invalid",  # Should be dict or StyleRule
        }

        with pytest.raises(ValueError) as exc_info:
            Theme.from_dict(data)

        assert "Invalid value for theme category" in str(exc_info.value)
        assert "error" in str(exc_info.value)

    def test_from_dict_with_style_rule_objects(self):
        """Test that from_dict accepts StyleRule objects."""
        data = {
            "error": StyleRule(fg_color="red", bold=True),
            "success": StyleRule(fg_color="green"),
        }
        theme = Theme.from_dict(data)

        assert theme.error.fg_color == "red"
        assert theme.error.bold is True
        assert theme.success.fg_color == "green"

    def test_partial_theme_from_dict(self):
        """Test creating a partial theme (only some categories specified)."""
        data = {
            "error": {"fg_color": "red", "bold": True},
        }
        theme = Theme.from_dict(data)

        # Specified category should be set
        assert theme.error.fg_color == "red"
        assert theme.error.bold is True

        # Unspecified categories should have defaults
        assert isinstance(theme.success, StyleRule)
        assert theme.success.fg_color is None

    def test_custom_theme_with_truecolor(self):
        """Test creating a custom theme with RGB truecolor values."""
        theme = Theme(
            error=StyleRule(fg_color=(255, 0, 0), bold=True),
            success=StyleRule(fg_color=(0, 255, 0)),
            info=StyleRule(fg_color=(100, 149, 237)),  # Cornflower blue
        )

        assert theme.error.fg_color == (255, 0, 0)
        assert theme.success.fg_color == (0, 255, 0)
        assert theme.info.fg_color == (100, 149, 237)

    def test_custom_theme_with_mixed_color_types(self):
        """Test theme with mixed color specification types."""
        theme = Theme(
            error=StyleRule(fg_color="red"),  # Named color
            success=StyleRule(fg_color=46),  # 256-color index
            info=StyleRule(fg_color=(0, 149, 255)),  # RGB truecolor
        )

        assert theme.error.fg_color == "red"
        assert theme.success.fg_color == 46
        assert theme.info.fg_color == (0, 149, 255)


class TestThemePresets:
    """Tests for all built-in theme presets."""

    def test_solarized_dark_preset(self):
        """Test Solarized Dark theme preset."""
        theme = Theme.solarized_dark()

        # Check it returns a Theme instance
        assert isinstance(theme, Theme)

        # Check a few key colors (256-color codes)
        assert theme.error.fg_color == 160  # Solarized red
        assert theme.success.fg_color == 100  # Solarized green
        assert theme.info.fg_color == 37  # Solarized cyan

        # Check bold attributes
        assert theme.user_message.bold is True
        assert theme.error.bold is True

    def test_solarized_light_preset(self):
        """Test Solarized Light theme preset."""
        theme = Theme.solarized_light()

        # Check it returns a Theme instance
        assert isinstance(theme, Theme)

        # Check same color codes as dark (but different base colors)
        assert theme.error.fg_color == 160  # Solarized red
        assert theme.success.fg_color == 100  # Solarized green
        assert theme.warning.fg_color == 136  # Solarized yellow

        # Check bold attributes
        assert theme.user_message.bold is True
        assert theme.warning.bold is True

    def test_gruvbox_preset(self):
        """Test Gruvbox theme preset."""
        theme = Theme.gruvbox()

        # Check it returns a Theme instance
        assert isinstance(theme, Theme)

        # Check Gruvbox-specific colors
        assert theme.error.fg_color == 167  # Gruvbox bright red
        assert theme.success.fg_color == 142  # Gruvbox bright green
        assert theme.warning.fg_color == 214  # Gruvbox bright yellow

        # Check styling
        assert theme.user_message.bold is True
        assert theme.thinking.italic is True

    def test_nord_preset(self):
        """Test Nord theme preset."""
        theme = Theme.nord()

        # Check it returns a Theme instance
        assert isinstance(theme, Theme)

        # Check Nord-specific colors
        assert theme.error.fg_color == 167  # Nord11 (red)
        assert theme.success.fg_color == 150  # Nord14 (green)
        assert theme.info.fg_color == 116  # Nord8 (cyan)

        # Check styling
        assert theme.tool_use.bold is True
        assert theme.thinking.italic is True

    def test_monochrome_preset(self):
        """Test monochrome theme preset."""
        theme = Theme.monochrome()

        # Check it returns a Theme instance
        assert isinstance(theme, Theme)

        # Monochrome should have NO colors, only styles
        assert theme.error.fg_color is None
        assert theme.success.fg_color is None
        assert theme.warning.fg_color is None
        assert theme.user_message.fg_color is None

        # But should have bold/dim/underline
        assert theme.user_message.bold is True
        assert theme.error.bold is True
        assert theme.error.underline is True
        assert theme.system_message.dim is True
        assert theme.thinking.italic is True

    def test_high_contrast_preset(self):
        """Test high contrast theme preset."""
        theme = Theme.high_contrast()

        # Check it returns a Theme instance
        assert isinstance(theme, Theme)

        # High contrast uses named bright colors
        assert theme.error.fg_color == "bright_red"
        assert theme.success.fg_color == "bright_green"
        assert theme.warning.fg_color == "bright_yellow"

        # Should have both bold AND underline for emphasis
        assert theme.error.bold is True
        assert theme.error.underline is True
        assert theme.warning.bold is True
        assert theme.warning.underline is True

    def test_all_presets_have_all_categories(self):
        """Test that all presets define all required categories."""
        presets = [
            Theme.claude_code_default(),
            Theme.solarized_dark(),
            Theme.solarized_light(),
            Theme.gruvbox(),
            Theme.nord(),
            Theme.monochrome(),
            Theme.high_contrast(),
        ]

        required_categories = [
            "user_message",
            "assistant_message",
            "system_message",
            "tool_use",
            "tool_result",
            "tool_error",
            "error",
            "warning",
            "success",
            "info",
            "debug",
            "bullet",
            "tree_connector",
            "metadata",
            "truncation",
            "code_block",
            "inline_code",
            "thinking",
            "cost_display",
        ]

        for theme in presets:
            for category in required_categories:
                assert hasattr(theme, category)
                assert isinstance(getattr(theme, category), StyleRule)

    def test_from_preset_solarized_dark(self):
        """Test loading Solarized Dark via from_preset."""
        theme = Theme.from_preset("solarized_dark")
        expected = Theme.solarized_dark()

        assert theme.error.fg_color == expected.error.fg_color
        assert theme.success.fg_color == expected.success.fg_color

    def test_from_preset_solarized_light(self):
        """Test loading Solarized Light via from_preset."""
        theme = Theme.from_preset("solarized_light")
        expected = Theme.solarized_light()

        assert theme.error.fg_color == expected.error.fg_color
        assert theme.success.fg_color == expected.success.fg_color

    def test_from_preset_gruvbox(self):
        """Test loading Gruvbox via from_preset."""
        theme = Theme.from_preset("gruvbox")
        expected = Theme.gruvbox()

        assert theme.error.fg_color == expected.error.fg_color
        assert theme.warning.fg_color == expected.warning.fg_color

    def test_from_preset_nord(self):
        """Test loading Nord via from_preset."""
        theme = Theme.from_preset("nord")
        expected = Theme.nord()

        assert theme.info.fg_color == expected.info.fg_color
        assert theme.success.fg_color == expected.success.fg_color

    def test_from_preset_monochrome(self):
        """Test loading monochrome via from_preset."""
        theme = Theme.from_preset("monochrome")
        expected = Theme.monochrome()

        # Check no colors
        assert theme.error.fg_color == expected.error.fg_color  # None
        assert theme.error.bold == expected.error.bold  # True

    def test_from_preset_high_contrast(self):
        """Test loading high contrast via from_preset."""
        theme = Theme.from_preset("high_contrast")
        expected = Theme.high_contrast()

        assert theme.error.fg_color == expected.error.fg_color
        assert theme.error.underline == expected.error.underline

    def test_from_preset_case_insensitive(self):
        """Test that preset names are case-insensitive."""
        theme1 = Theme.from_preset("GRUVBOX")
        theme2 = Theme.from_preset("gruvbox")
        theme3 = Theme.from_preset("GruvBox")

        assert theme1.error.fg_color == theme2.error.fg_color == theme3.error.fg_color

    def test_from_preset_unknown_raises_error(self):
        """Test that unknown preset name raises ValueError with helpful message."""
        with pytest.raises(ValueError) as exc_info:
            Theme.from_preset("unknown_theme")

        error_msg = str(exc_info.value)
        assert "Unknown theme preset: 'unknown_theme'" in error_msg
        assert "Available:" in error_msg
        assert "claude_code" in error_msg
        assert "solarized_dark" in error_msg
        assert "gruvbox" in error_msg

    def test_all_presets_accessible_via_from_preset(self):
        """Test that all preset methods are accessible via from_preset."""
        preset_names = [
            "claude_code",
            "claude_code_default",
            "solarized_dark",
            "solarized_light",
            "gruvbox",
            "nord",
            "monochrome",
            "high_contrast",
        ]

        for name in preset_names:
            theme = Theme.from_preset(name)
            assert isinstance(theme, Theme)
