"""Tests for semantic UI element formatter (Story 4.6).

Tests terminal capability detection, color theming, and ANSI formatting
for semantic roles. Validates research findings from Claude Code CLI
architecture analysis.
"""



from claude_agent_sdk.rendering.semantic import (
    ANSIFormatter,
    ColorTheme,
    FormatterConfig,
    SemanticRole,
    TerminalCapability,
    default_theme,
    detect_capability,
)


class TestTerminalCapability:
    """Tests for terminal capability detection."""

    def test_no_color_env_disables_color(self, monkeypatch):
        """NO_COLOR environment variable should disable all color."""
        monkeypatch.setenv("NO_COLOR", "1")
        assert detect_capability() == TerminalCapability.MONOCHROME

    def test_colorterm_truecolor_detection(self, monkeypatch):
        """COLORTERM=truecolor should enable 24-bit RGB."""
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("COLORTERM", "truecolor")
        assert detect_capability() == TerminalCapability.TRUECOLOR

    def test_colorterm_24bit_detection(self, monkeypatch):
        """COLORTERM=24bit should enable 24-bit RGB."""
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("COLORTERM", "24bit")
        assert detect_capability() == TerminalCapability.TRUECOLOR

    def test_term_256color_detection(self, monkeypatch):
        """TERM=xterm-256color should enable 256-color mode."""
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("COLORTERM", raising=False)
        monkeypatch.setenv("TERM", "xterm-256color")
        assert detect_capability() == TerminalCapability.COLOR_256

    def test_term_color_detection(self, monkeypatch):
        """TERM=xterm-color should enable 16-color mode."""
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("COLORTERM", raising=False)
        monkeypatch.setenv("TERM", "xterm-color")
        assert detect_capability() == TerminalCapability.COLOR_16

    def test_capability_comparison(self):
        """Test capability ordering for fallback logic."""
        # Higher capability < lower capability (inverted for fallback logic)
        assert TerminalCapability.MONOCHROME < TerminalCapability.COLOR_16
        assert TerminalCapability.COLOR_16 < TerminalCapability.COLOR_256
        assert TerminalCapability.COLOR_256 < TerminalCapability.TRUECOLOR


class TestColorTheme:
    """Tests for color theme functionality."""

    def test_default_theme_has_all_roles(self):
        """Default theme should map all 10 semantic roles."""
        theme = default_theme()
        assert theme.name == "Claude Code Default"
        assert len(theme.colors) == 10  # All 10 roles

        # Verify all roles have mappings
        for role in SemanticRole:
            assert role in theme.colors

    def test_default_theme_research_validated_colors(self):
        """Default theme colors should match research findings."""
        theme = default_theme()

        # Research-validated mappings from Story 1
        assert theme.colors[SemanticRole.ERROR] == "\033[31;1m"  # Bright red (bold)
        assert theme.colors[SemanticRole.WARNING] == "\033[33;1m"  # Bright yellow (bold)
        assert theme.colors[SemanticRole.SUCCESS] == "\033[32;1m"  # Bright green (bold)
        assert theme.colors[SemanticRole.INFO] == "\033[36m"  # Cyan
        assert theme.colors[SemanticRole.SYSTEM] == "\033[36m"  # Cyan
        assert theme.colors[SemanticRole.TOOL] == "\033[35m"  # Magenta
        assert theme.colors[SemanticRole.INTERACTIVE] == "\033[34m"  # Blue

    def test_theme_get_color(self):
        """Theme get_color() should return correct ANSI codes."""
        theme = default_theme()
        error_color = theme.get_color(SemanticRole.ERROR)
        assert error_color == "\033[31;1m"

    def test_theme_get_color_fallback(self):
        """Theme get_color() should use fallback for missing roles."""
        theme = ColorTheme(name="Test", colors={}, fallback_color="\033[0m")
        assert theme.get_color(SemanticRole.ERROR) == "\033[0m"

    def test_theme_customization(self):
        """Theme customize() should create new theme with overrides."""
        base = default_theme()
        original_error = base.colors[SemanticRole.ERROR]

        custom = base.customize({SemanticRole.ERROR: "\033[91m"})

        # Custom theme should have override
        assert custom.colors[SemanticRole.ERROR] == "\033[91m"
        # Other colors should be inherited
        assert custom.colors[SemanticRole.WARNING] == base.colors[SemanticRole.WARNING]
        # Original theme should be unchanged
        assert base.colors[SemanticRole.ERROR] == original_error


class TestANSIFormatter:
    """Tests for ANSI formatter functionality."""

    def test_formatter_basic_formatting(self):
        """Formatter should apply ANSI codes correctly."""
        formatter = ANSIFormatter()
        result = formatter.format("Error message", SemanticRole.ERROR)

        # Should have combined ANSI sequence (research requirement)
        assert "\033[31;1m" in result  # Bright red
        assert "\033[0m" in result  # Reset
        assert "Error message" in result

    def test_formatter_combined_ansi_sequences(self):
        """Formatter should use combined ANSI sequences (Issue #6466 pattern)."""
        formatter = ANSIFormatter()
        result = formatter.format("Test", SemanticRole.ERROR)

        # Should use combined sequence (\033[31;1m) NOT separate (\033[31m\033[1m)
        assert "\033[31;1m" in result
        # Should only have 2 escape sequences: color + reset
        assert result.count("\033[") == 2

    def test_formatter_all_semantic_roles(self):
        """Formatter should handle all 10 semantic roles."""
        formatter = ANSIFormatter()

        for role in SemanticRole:
            result = formatter.format("Test", role)
            # Should contain reset code
            assert "\033[0m" in result
            # Should contain original text
            assert "Test" in result

    def test_formatter_with_icon(self):
        """Formatter should add icon prefix when requested."""
        formatter = ANSIFormatter()
        result = formatter.format_with_icon("Failed", SemanticRole.ERROR)

        # Should include icon from role
        assert SemanticRole.ERROR.default_icon in result
        # Should include message
        assert "Failed" in result
        # Should have color codes
        assert "\033[31;1m" in result

    def test_formatter_with_custom_icon(self):
        """Formatter should use custom icon when provided."""
        formatter = ANSIFormatter()
        result = formatter.format_with_icon("Test", SemanticRole.ERROR, icon="🔥")

        # Should use custom icon instead of default
        assert "🔥" in result
        assert "Test" in result

    def test_formatter_monochrome_mode(self):
        """Formatter should disable colors in monochrome mode."""
        config = FormatterConfig(force_capability=TerminalCapability.MONOCHROME)
        formatter = ANSIFormatter(config=config)
        result = formatter.format("Test", SemanticRole.ERROR)

        # Should have NO color codes
        assert "\033[" not in result
        assert result == "Test"

    def test_formatter_color_disabled(self):
        """Formatter should respect enable_color=False."""
        config = FormatterConfig(enable_color=False)
        formatter = ANSIFormatter(config=config)
        result = formatter.format("Test", SemanticRole.ERROR)

        # Should have NO color codes
        assert "\033[" not in result
        assert result == "Test"

    def test_formatter_custom_theme(self):
        """Formatter should use custom theme colors."""
        custom_theme = ColorTheme(
            name="Test Theme",
            colors={SemanticRole.ERROR: "\033[91m"},  # Different red
        )
        config = FormatterConfig(theme=custom_theme)
        formatter = ANSIFormatter(config=config)
        result = formatter.format("Test", SemanticRole.ERROR)

        # Should use custom color
        assert "\033[91m" in result

    def test_formatter_theme_customization_method(self):
        """Formatter customize_theme() should create new formatter."""
        base = ANSIFormatter()
        custom = base.customize_theme({SemanticRole.ERROR: "\033[91m"})

        # Should be a new instance
        assert custom is not base

        # Should use new color
        result = custom.format("Test", SemanticRole.ERROR)
        assert "\033[91m" in result

    def test_formatter_respects_terminal_capability(self):
        """Formatter should respect terminal capability setting."""
        config = FormatterConfig(force_capability=TerminalCapability.COLOR_16)
        formatter = ANSIFormatter(config=config)

        # Capability should be set correctly
        assert formatter.capability == TerminalCapability.COLOR_16

    def test_formatter_default_config(self):
        """Formatter should use default config when none provided."""
        formatter = ANSIFormatter()

        # Should have default theme
        assert formatter.config.theme is not None
        assert formatter.config.enable_color is True
        assert formatter.config.respect_no_color is True

    def test_formatter_preserves_multiline_content(self):
        """Formatter should handle multiline content correctly."""
        formatter = ANSIFormatter()
        multiline = "Line 1\nLine 2\nLine 3"
        result = formatter.format(multiline, SemanticRole.ERROR)

        # Should preserve newlines
        assert "Line 1\nLine 2\nLine 3" in result
        # Should have color codes
        assert "\033[31;1m" in result

    def test_formatter_handles_empty_content(self):
        """Formatter should handle empty content gracefully."""
        formatter = ANSIFormatter()
        result = formatter.format("", SemanticRole.ERROR)

        # Should still have color codes
        assert "\033[31;1m" in result
        assert "\033[0m" in result


class TestFormatterConfig:
    """Tests for formatter configuration."""

    def test_config_default_theme(self):
        """Config should initialize default theme if none provided."""
        config = FormatterConfig()
        assert config.theme is not None
        assert config.theme.name == "Claude Code Default"

    def test_config_custom_theme(self):
        """Config should accept custom theme."""
        custom_theme = ColorTheme(name="Custom", colors={})
        config = FormatterConfig(theme=custom_theme)
        assert config.theme.name == "Custom"

    def test_config_all_options(self):
        """Config should accept all configuration options."""
        config = FormatterConfig(
            enable_color=False,
            theme=ColorTheme(name="Test", colors={}),
            force_capability=TerminalCapability.COLOR_256,
            respect_no_color=False,
        )

        assert config.enable_color is False
        assert config.theme.name == "Test"
        assert config.force_capability == TerminalCapability.COLOR_256
        assert config.respect_no_color is False


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_complete_formatting_workflow(self):
        """Test complete workflow: detect + format."""
        # Create formatter with default config
        formatter = ANSIFormatter()

        # Format error message
        error_msg = formatter.format("Operation failed", SemanticRole.ERROR)

        # Should be properly formatted
        assert "\033[31;1m" in error_msg
        assert "Operation failed" in error_msg
        assert "\033[0m" in error_msg

    def test_workflow_with_theme_customization(self):
        """Test workflow with custom theme."""
        # Create custom theme
        theme = default_theme().customize({SemanticRole.ERROR: "\033[91m"})

        # Create formatter
        formatter = ANSIFormatter(config=FormatterConfig(theme=theme))

        # Format message
        result = formatter.format("Error", SemanticRole.ERROR)

        # Should use custom color
        assert "\033[91m" in result

    def test_workflow_monochrome_fallback(self, monkeypatch):
        """Test workflow with monochrome fallback."""
        # Simulate monochrome terminal
        monkeypatch.setenv("NO_COLOR", "1")

        # Create formatter (should auto-detect)
        config = FormatterConfig(force_capability=TerminalCapability.MONOCHROME)
        formatter = ANSIFormatter(config=config)

        # Format message
        result = formatter.format("Test", SemanticRole.ERROR)

        # Should have no colors
        assert "\033[" not in result
        assert result == "Test"
