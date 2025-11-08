"""Unit tests for ANSI encoder with terminal detection."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from claude_agent_sdk.rendering.ansi import (
    BASIC_BG_COLORS,
    BASIC_COLORS,
    AnsiEncoder,
    detect_color_depth,
    rgb_to_16,
    rgb_to_256,
)
from claude_agent_sdk.rendering.theme import ColorDepth, StyleRule


class TestColorConversion:
    """Test RGB to 256-color and 16-color conversion functions."""

    def test_rgb_to_256_grayscale(self) -> None:
        """Test RGB to 256-color conversion for grayscale values."""
        # Pure black -> basic black
        assert rgb_to_256(0, 0, 0) == 16

        # Pure white -> RGB cube white
        assert rgb_to_256(255, 255, 255) == 231

        # Mid-gray -> grayscale ramp
        gray_idx = rgb_to_256(128, 128, 128)
        assert 232 <= gray_idx <= 255

    def test_rgb_to_256_primary_colors(self) -> None:
        """Test RGB to 256-color conversion for primary colors."""
        # Pure red (brightest)
        red_idx = rgb_to_256(255, 0, 0)
        assert red_idx == 16 + (36 * 5) + (6 * 0) + 0  # 196

        # Pure green (brightest)
        green_idx = rgb_to_256(0, 255, 0)
        assert green_idx == 16 + (36 * 0) + (6 * 5) + 0  # 46

        # Pure blue (brightest)
        blue_idx = rgb_to_256(0, 0, 255)
        assert blue_idx == 16 + (36 * 0) + (6 * 0) + 5  # 21

    def test_rgb_to_256_mixed_colors(self) -> None:
        """Test RGB to 256-color conversion for mixed colors."""
        # Yellow (red + green)
        yellow_idx = rgb_to_256(255, 255, 0)
        assert yellow_idx == 16 + (36 * 5) + (6 * 5) + 0  # 226

        # Magenta (red + blue)
        magenta_idx = rgb_to_256(255, 0, 255)
        assert magenta_idx == 16 + (36 * 5) + (6 * 0) + 5  # 201

        # Cyan (green + blue)
        cyan_idx = rgb_to_256(0, 255, 255)
        assert cyan_idx == 16 + (36 * 0) + (6 * 5) + 5  # 51

    def test_rgb_to_16_grayscale(self) -> None:
        """Test RGB to 16-color conversion for grayscale values."""
        # Dark gray -> white
        assert rgb_to_16(64, 64, 64) == BASIC_COLORS["white"]

        # Light gray -> bright white
        assert rgb_to_16(192, 192, 192) == BASIC_COLORS["bright_white"]

    def test_rgb_to_16_primary_colors(self) -> None:
        """Test RGB to 16-color conversion for primary colors."""
        # Bright red
        assert rgb_to_16(255, 0, 0) == BASIC_COLORS["bright_red"]

        # Dim red
        assert rgb_to_16(100, 0, 0) == BASIC_COLORS["red"]

        # Bright green
        assert rgb_to_16(0, 255, 0) == BASIC_COLORS["bright_green"]

        # Bright blue
        assert rgb_to_16(0, 0, 255) == BASIC_COLORS["bright_blue"]

    def test_rgb_to_16_mixed_colors(self) -> None:
        """Test RGB to 16-color conversion for mixed colors."""
        # Yellow (red + green)
        assert rgb_to_16(255, 255, 0) == BASIC_COLORS["bright_yellow"]

        # Magenta (red + blue)
        assert rgb_to_16(255, 0, 255) == BASIC_COLORS["bright_magenta"]

        # Cyan (green + blue)
        assert rgb_to_16(0, 255, 255) == BASIC_COLORS["bright_cyan"]


class TestTerminalDetection:
    """Test terminal capability detection."""

    @patch("sys.stdout.isatty")
    def test_detect_no_tty(self, mock_isatty: MagicMock) -> None:
        """Test color detection returns NONE when not a TTY."""
        mock_isatty.return_value = False
        assert detect_color_depth() == ColorDepth.NONE

    @patch("sys.stdout.isatty")
    @patch.dict(os.environ, {"COLORTERM": "truecolor"}, clear=True)
    def test_detect_truecolor_via_colorterm(self, mock_isatty: MagicMock) -> None:
        """Test truecolor detection via COLORTERM environment variable."""
        mock_isatty.return_value = True
        assert detect_color_depth() == ColorDepth.TRUECOLOR

    @patch("sys.stdout.isatty")
    @patch.dict(os.environ, {"TERM": "xterm-truecolor"}, clear=True)
    def test_detect_truecolor_via_term(self, mock_isatty: MagicMock) -> None:
        """Test truecolor detection via TERM environment variable."""
        mock_isatty.return_value = True
        assert detect_color_depth() == ColorDepth.TRUECOLOR

    @patch("sys.stdout.isatty")
    @patch.dict(os.environ, {"TERM_PROGRAM": "vscode"}, clear=True)
    def test_detect_truecolor_via_term_program(self, mock_isatty: MagicMock) -> None:
        """Test truecolor detection via TERM_PROGRAM environment variable."""
        mock_isatty.return_value = True
        assert detect_color_depth() == ColorDepth.TRUECOLOR

    @patch("sys.stdout.isatty")
    @patch.dict(os.environ, {"WT_SESSION": "some-guid"}, clear=True)
    def test_detect_truecolor_windows_terminal(self, mock_isatty: MagicMock) -> None:
        """Test truecolor detection for Windows Terminal."""
        mock_isatty.return_value = True
        assert detect_color_depth() == ColorDepth.TRUECOLOR

    @patch("sys.stdout.isatty")
    @patch("subprocess.run")
    @patch.dict(os.environ, {}, clear=True)
    def test_detect_256_via_tput(
        self, mock_run: MagicMock, mock_isatty: MagicMock
    ) -> None:
        """Test 256-color detection via tput."""
        mock_isatty.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout="256\n")
        assert detect_color_depth() == ColorDepth.EXTENDED_256

    @patch("sys.stdout.isatty")
    @patch("subprocess.run")
    @patch.dict(os.environ, {}, clear=True)
    def test_detect_16_via_tput(
        self, mock_run: MagicMock, mock_isatty: MagicMock
    ) -> None:
        """Test 16-color detection via tput."""
        mock_isatty.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout="16\n")
        assert detect_color_depth() == ColorDepth.BASIC_16

    @patch("sys.stdout.isatty")
    @patch("subprocess.run")
    @patch.dict(os.environ, {}, clear=True)
    def test_detect_8_colors_treated_as_16(
        self, mock_run: MagicMock, mock_isatty: MagicMock
    ) -> None:
        """Test 8-color terminals are treated as 16-color."""
        mock_isatty.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout="8\n")
        assert detect_color_depth() == ColorDepth.BASIC_16

    @patch("sys.stdout.isatty")
    @patch("subprocess.run")
    @patch.dict(os.environ, {"TERM": "xterm"}, clear=True)
    def test_detect_fallback_with_term(
        self, mock_run: MagicMock, mock_isatty: MagicMock
    ) -> None:
        """Test fallback to BASIC_16 when TERM is set but tput fails."""
        mock_isatty.return_value = True
        mock_run.side_effect = FileNotFoundError("tput not found")
        assert detect_color_depth() == ColorDepth.BASIC_16

    @patch("sys.stdout.isatty")
    @patch("subprocess.run")
    @patch.dict(os.environ, {}, clear=True)
    def test_detect_none_when_no_term(
        self, mock_run: MagicMock, mock_isatty: MagicMock
    ) -> None:
        """Test NONE detection when TERM not set and tput unavailable."""
        mock_isatty.return_value = True
        mock_run.side_effect = FileNotFoundError("tput not found")
        assert detect_color_depth() == ColorDepth.NONE


class TestAnsiEncoder:
    """Test AnsiEncoder class."""

    def test_init_auto_detect(self) -> None:
        """Test encoder initializes with auto-detected color depth."""
        encoder = AnsiEncoder()
        assert encoder.color_depth in ColorDepth

    def test_init_explicit_depth(self) -> None:
        """Test encoder initializes with explicit color depth."""
        encoder = AnsiEncoder(ColorDepth.EXTENDED_256)
        assert encoder.color_depth == ColorDepth.EXTENDED_256

    def test_encode_no_color(self) -> None:
        """Test encoding returns plain text when color is disabled."""
        encoder = AnsiEncoder(ColorDepth.NONE)
        rule = StyleRule(fg_color="red", bold=True)
        result = encoder.encode("Hello", rule)
        assert result == "Hello"

    def test_encode_bold_only(self) -> None:
        """Test encoding with bold style only."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(bold=True)
        result = encoder.encode("Hello", rule)
        assert result == "\033[1mHello\033[0m"

    def test_encode_dim_only(self) -> None:
        """Test encoding with dim style only."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(dim=True)
        result = encoder.encode("Hello", rule)
        assert result == "\033[2mHello\033[0m"

    def test_encode_italic_only(self) -> None:
        """Test encoding with italic style only."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(italic=True)
        result = encoder.encode("Hello", rule)
        assert result == "\033[3mHello\033[0m"

    def test_encode_underline_only(self) -> None:
        """Test encoding with underline style only."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(underline=True)
        result = encoder.encode("Hello", rule)
        assert result == "\033[4mHello\033[0m"

    def test_encode_named_color_16(self) -> None:
        """Test encoding named colors in 16-color mode."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)

        # Red foreground
        rule = StyleRule(fg_color="red")
        result = encoder.encode("Error", rule)
        assert result == "\033[31mError\033[0m"

        # Bright green foreground
        rule = StyleRule(fg_color="bright_green")
        result = encoder.encode("Success", rule)
        assert result == "\033[92mSuccess\033[0m"

    def test_encode_named_color_background(self) -> None:
        """Test encoding named background colors."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(bg_color="blue")
        result = encoder.encode("Text", rule)
        assert result == "\033[44mText\033[0m"

    def test_encode_rgb_truecolor(self) -> None:
        """Test encoding RGB colors in truecolor mode."""
        encoder = AnsiEncoder(ColorDepth.TRUECOLOR)
        rule = StyleRule(fg_color=(255, 0, 0))  # Red
        result = encoder.encode("Red", rule)
        assert result == "\033[38;2;255;0;0mRed\033[0m"

    def test_encode_rgb_256(self) -> None:
        """Test encoding RGB colors in 256-color mode."""
        encoder = AnsiEncoder(ColorDepth.EXTENDED_256)
        rule = StyleRule(fg_color=(255, 0, 0))  # Red
        result = encoder.encode("Red", rule)
        # Should convert to 256-color index 196
        assert result == "\033[38;5;196mRed\033[0m"

    def test_encode_rgb_16(self) -> None:
        """Test encoding RGB colors in 16-color mode."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(fg_color=(255, 0, 0))  # Red
        result = encoder.encode("Red", rule)
        # Should convert to bright red (91)
        assert result == "\033[91mRed\033[0m"

    def test_encode_256_color_index(self) -> None:
        """Test encoding with 256-color palette index."""
        encoder = AnsiEncoder(ColorDepth.EXTENDED_256)
        rule = StyleRule(fg_color=196)  # Red in 256-color palette
        result = encoder.encode("Red", rule)
        assert result == "\033[38;5;196mRed\033[0m"

    def test_encode_combined_styles(self) -> None:
        """Test encoding with multiple style attributes."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(fg_color="red", bg_color="white", bold=True, underline=True)
        result = encoder.encode("Alert", rule)
        # Should have codes for bold (1), underline (4), fg (31), bg (47)
        assert "\033[" in result
        assert "1" in result
        assert "4" in result
        assert "31" in result
        assert "47" in result
        assert "Alert" in result
        assert "\033[0m" in result

    def test_encode_empty_rule(self) -> None:
        """Test encoding with empty style rule returns plain text."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule()
        result = encoder.encode("Plain", rule)
        assert result == "Plain"

    def test_encode_invalid_rgb_tuple(self) -> None:
        """Test encoding with invalid RGB tuple length."""
        encoder = AnsiEncoder(ColorDepth.TRUECOLOR)
        rule = StyleRule(fg_color=(255, 0))  # type: ignore[arg-type]
        result = encoder.encode("Text", rule)
        # Should return unstyled text (no color code)
        assert result == "Text"

    def test_encode_invalid_color_index(self) -> None:
        """Test encoding with out-of-range color index."""
        encoder = AnsiEncoder(ColorDepth.EXTENDED_256)
        rule = StyleRule(fg_color=999)  # Out of range
        result = encoder.encode("Text", rule)
        # Should return unstyled text
        assert result == "Text"

    def test_encode_unknown_named_color(self) -> None:
        """Test encoding with unknown named color."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(fg_color="foobar")
        result = encoder.encode("Text", rule)
        # Should return unstyled text
        assert result == "Text"

    def test_encode_256_to_16_degradation(self) -> None:
        """Test 256-color index degrades to 16-color."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(fg_color=196)  # 256-color red
        result = encoder.encode("Text", rule)
        # Should degrade to basic red (code 31-37 or 90-97)
        assert "\033[" in result
        assert result.endswith("\033[0m")

    def test_encode_background_rgb_truecolor(self) -> None:
        """Test encoding RGB background in truecolor mode."""
        encoder = AnsiEncoder(ColorDepth.TRUECOLOR)
        rule = StyleRule(bg_color=(0, 255, 0))  # Green
        result = encoder.encode("Text", rule)
        assert result == "\033[48;2;0;255;0mText\033[0m"

    def test_encode_background_256(self) -> None:
        """Test encoding background in 256-color mode."""
        encoder = AnsiEncoder(ColorDepth.EXTENDED_256)
        rule = StyleRule(bg_color=46)  # Green
        result = encoder.encode("Text", rule)
        assert result == "\033[48;5;46mText\033[0m"


class TestNamedColorMappings:
    """Test named color mapping dictionaries."""

    def test_basic_colors_completeness(self) -> None:
        """Test BASIC_COLORS contains all expected colors."""
        expected_colors = {
            "black",
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            "bright_black",
            "bright_red",
            "bright_green",
            "bright_yellow",
            "bright_blue",
            "bright_magenta",
            "bright_cyan",
            "bright_white",
        }
        assert set(BASIC_COLORS.keys()) == expected_colors

    def test_basic_colors_code_ranges(self) -> None:
        """Test BASIC_COLORS codes are in valid ranges."""
        for color, code in BASIC_COLORS.items():
            if color.startswith("bright_"):
                assert 90 <= code <= 97
            else:
                assert 30 <= code <= 37

    def test_basic_bg_colors_offset(self) -> None:
        """Test BASIC_BG_COLORS are offset by 10 from foreground."""
        for color, fg_code in BASIC_COLORS.items():
            bg_code = BASIC_BG_COLORS[color]
            assert bg_code == fg_code + 10


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_encode_multiline_text(self) -> None:
        """Test encoding preserves multiline text."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(fg_color="red")
        text = "Line 1\nLine 2\nLine 3"
        result = encoder.encode(text, rule)
        assert "Line 1\nLine 2\nLine 3" in result
        assert result.startswith("\033[")
        assert result.endswith("\033[0m")

    def test_encode_empty_text(self) -> None:
        """Test encoding empty string."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(fg_color="red")
        result = encoder.encode("", rule)
        assert result == "\033[31m\033[0m"

    def test_encode_unicode_text(self) -> None:
        """Test encoding handles Unicode text."""
        encoder = AnsiEncoder(ColorDepth.BASIC_16)
        rule = StyleRule(fg_color="blue")
        text = "Hello 世界 🌍"
        result = encoder.encode(text, rule)
        assert text in result
        assert result.startswith("\033[")
        assert result.endswith("\033[0m")

    def test_rgb_conversion_boundary_values(self) -> None:
        """Test RGB conversion with boundary values."""
        # All zeros
        assert rgb_to_256(0, 0, 0) == 16
        assert rgb_to_16(0, 0, 0) in BASIC_COLORS.values()

        # All max
        assert rgb_to_256(255, 255, 255) == 231
        assert rgb_to_16(255, 255, 255) in BASIC_COLORS.values()

        # Mixed boundaries
        assert isinstance(rgb_to_256(255, 0, 0), int)
        assert isinstance(rgb_to_16(0, 255, 0), int)
