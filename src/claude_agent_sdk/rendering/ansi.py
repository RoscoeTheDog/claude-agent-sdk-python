"""ANSI escape sequence encoder with terminal capability detection.

This module provides the AnsiEncoder class that converts StyleRule objects
into ANSI escape sequences, with automatic terminal detection and graceful
degradation across color depths (truecolor → 256-color → 16-color → none).
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from claude_agent_sdk.rendering.theme import ColorDepth, StyleRule


# Named color mappings for 16-color mode
BASIC_COLORS = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "bright_black": 90,
    "bright_red": 91,
    "bright_green": 92,
    "bright_yellow": 93,
    "bright_blue": 94,
    "bright_magenta": 95,
    "bright_cyan": 96,
    "bright_white": 97,
}

# Background variants (add 10 to foreground codes)
BASIC_BG_COLORS = {name: code + 10 for name, code in BASIC_COLORS.items()}


def detect_color_depth() -> ColorDepth:
    """Detect terminal color capability.

    Detection strategy:
    1. Check if stdout is a TTY (return NONE if not)
    2. Check TERM/TERM_PROGRAM for truecolor support
    3. Run 'tput colors' to get numeric capability
    4. Fall back to BASIC_16 if uncertain

    Returns:
        ColorDepth enum value representing terminal capability
    """
    from claude_agent_sdk.rendering.theme import ColorDepth

    # Check if stdout is a TTY
    if not sys.stdout.isatty():
        return ColorDepth.NONE

    # Check for truecolor support via environment variables
    if _supports_truecolor():
        return ColorDepth.TRUECOLOR

    # Try tput to get color count
    try:
        result = subprocess.run(
            ["tput", "colors"],
            capture_output=True,
            text=True,
            timeout=1.0,
            check=False,
        )
        if result.returncode == 0:
            colors = int(result.stdout.strip())
            if colors >= 256:
                return ColorDepth.EXTENDED_256
            elif colors >= 16:
                return ColorDepth.BASIC_16
            elif colors >= 8:
                return ColorDepth.BASIC_16  # Treat 8-color as 16-color
            else:
                return ColorDepth.NONE
    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        ValueError,
        FileNotFoundError,
    ):
        # tput not available or failed, continue to fallback logic
        pass

    # Fallback: if TERM is set, assume at least 16-color support
    if os.environ.get("TERM"):
        return ColorDepth.BASIC_16

    return ColorDepth.NONE


def _supports_truecolor() -> bool:
    """Check if terminal supports 24-bit truecolor.

    Checks TERM and TERM_PROGRAM environment variables for indicators
    of truecolor support.

    Returns:
        True if truecolor is likely supported
    """
    term = os.environ.get("TERM", "").lower()
    term_program = os.environ.get("TERM_PROGRAM", "").lower()

    # Check for explicit truecolor indicators in TERM
    if "truecolor" in term or "24bit" in term:
        return True

    # Check for specific terminal programs known to support truecolor
    truecolor_terminals = {
        "iterm.app",
        "vscode",
        "hyper",
        "wezterm",
        "alacritty",
        "kitty",
    }
    if term_program in truecolor_terminals:
        return True

    # Windows Terminal supports truecolor
    if os.environ.get("WT_SESSION"):
        return True

    # Check for COLORTERM=truecolor
    colorterm = os.environ.get("COLORTERM", "").lower()
    return colorterm in ("truecolor", "24bit")


def rgb_to_256(r: int, g: int, b: int) -> int:
    """Convert RGB color to closest 256-color palette index.

    The 256-color palette consists of:
    - 0-15: Basic 16 colors
    - 16-231: 6x6x6 RGB cube (216 colors)
    - 232-255: Grayscale ramp (24 shades)

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        256-color palette index (0-255)
    """
    # Check if color is grayscale
    if r == g == b:
        # Use grayscale ramp (232-255)
        if r < 8:
            return 16  # Black from basic colors
        if r > 248:
            return 231  # White from RGB cube
        # Map to grayscale ramp: 232 + (0-23)
        return 232 + ((r - 8) * 24 // 240)

    # Map to 6x6x6 RGB cube (16-231)
    # Each component maps to 0-5
    r_idx = (r * 6) // 256
    g_idx = (g * 6) // 256
    b_idx = (b * 6) // 256

    return 16 + (36 * r_idx) + (6 * g_idx) + b_idx


def rgb_to_16(r: int, g: int, b: int) -> int:
    """Convert RGB color to closest 16-color ANSI code.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        ANSI color code (30-37 for normal, 90-97 for bright)
    """
    # Find dominant color
    max_component = max(r, g, b)
    min_component = min(r, g, b)

    # Check for grayscale
    if max_component - min_component < 30:
        # Grayscale - use average brightness
        brightness = (r + g + b) // 3
        return (
            BASIC_COLORS["bright_white"] if brightness > 128 else BASIC_COLORS["white"]
        )

    # For chromatic colors, use max component to determine brightness
    use_bright = max_component > 128

    # Determine dominant color(s)
    colors = []
    if r >= max_component * 0.8:
        colors.append("red")
    if g >= max_component * 0.8:
        colors.append("green")
    if b >= max_component * 0.8:
        colors.append("blue")

    # Map combinations to named colors
    if len(colors) == 3:
        color_name = "white"
    elif len(colors) == 2:
        if "red" in colors and "green" in colors:
            color_name = "yellow"
        elif "red" in colors and "blue" in colors:
            color_name = "magenta"
        elif "green" in colors and "blue" in colors:
            color_name = "cyan"
        else:
            color_name = "white"
    elif len(colors) == 1:
        color_name = colors[0]
    else:
        color_name = "white"

    # Add bright prefix if needed
    if use_bright and color_name not in ("white", "black"):
        color_name = f"bright_{color_name}"

    return BASIC_COLORS.get(color_name, BASIC_COLORS["white"])


class AnsiEncoder:
    """Encoder that converts StyleRule objects to ANSI escape sequences.

    This class handles terminal capability detection and graceful degradation
    across different color depths. It converts semantic style rules into
    appropriate ANSI escape codes based on the terminal's capabilities.

    Attributes:
        color_depth: Terminal color capability level
    """

    def __init__(self, color_depth: ColorDepth | None = None):
        """Initialize the ANSI encoder.

        Args:
            color_depth: Terminal color capability. If None, auto-detect.
        """

        if color_depth is None:
            color_depth = detect_color_depth()
        self.color_depth = color_depth

    def encode(self, text: str, rule: StyleRule) -> str:
        """Convert text and style rule to ANSI-styled string.

        Args:
            text: Text content to style
            rule: Style rule defining visual appearance

        Returns:
            Text wrapped in ANSI escape sequences, or plain text if color disabled
        """
        from claude_agent_sdk.rendering.theme import ColorDepth

        if self.color_depth == ColorDepth.NONE:
            return text

        codes = []

        # Font styles
        if rule.bold:
            codes.append("1")
        if rule.dim:
            codes.append("2")
        if rule.italic:
            codes.append("3")
        if rule.underline:
            codes.append("4")

        # Foreground color
        if rule.fg_color is not None:
            fg_code = self._encode_color(rule.fg_color, foreground=True)
            if fg_code:
                codes.append(fg_code)

        # Background color
        if rule.bg_color is not None:
            bg_code = self._encode_color(rule.bg_color, foreground=False)
            if bg_code:
                codes.append(bg_code)

        # If no codes, return unstyled text
        if not codes:
            return text

        # Build ANSI escape sequence: \033[{codes}m{text}\033[0m
        escape = f"\033[{';'.join(codes)}m"
        reset = "\033[0m"
        return f"{escape}{text}{reset}"

    def _encode_color(
        self, color: str | tuple[int, int, int] | int, foreground: bool
    ) -> str:
        """Encode a color value to ANSI color code.

        Args:
            color: Color as named string, RGB tuple, or 256-color index
            foreground: True for foreground color, False for background

        Returns:
            ANSI color code string (e.g., "38;5;196" for 256-color red)
        """

        # Handle RGB tuple
        if isinstance(color, tuple):
            if len(color) == 3:
                r, g, b = color
                return self._encode_rgb(r, g, b, foreground)
            # Invalid tuple length - defensive check for runtime safety
            return ""  # type: ignore[unreachable]
        # Handle 256-color index
        if isinstance(color, int):
            if 0 <= color <= 255:
                return self._encode_256(color, foreground)
            # Invalid color index, return empty string
            return ""
        # Handle named color - color must be str at this point
        return self._encode_named(color, foreground)

    def _encode_rgb(self, r: int, g: int, b: int, foreground: bool) -> str:
        """Encode RGB color with appropriate degradation.

        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            foreground: True for foreground, False for background

        Returns:
            ANSI color code string
        """
        from claude_agent_sdk.rendering.theme import ColorDepth

        if self.color_depth == ColorDepth.TRUECOLOR:
            # Use 24-bit truecolor: 38;2;R;G;B or 48;2;R;G;B
            prefix = "38" if foreground else "48"
            return f"{prefix};2;{r};{g};{b}"

        elif self.color_depth == ColorDepth.EXTENDED_256:
            # Convert to 256-color
            color_idx = rgb_to_256(r, g, b)
            return self._encode_256(color_idx, foreground)

        elif self.color_depth == ColorDepth.BASIC_16:
            # Convert to 16-color
            code = rgb_to_16(r, g, b)
            if not foreground:
                code += 10  # Background codes are +10
            return str(code)

        return ""

    def _encode_256(self, color_idx: int, foreground: bool) -> str:
        """Encode 256-color palette index.

        Args:
            color_idx: Color index (0-255)
            foreground: True for foreground, False for background

        Returns:
            ANSI color code string
        """
        from claude_agent_sdk.rendering.theme import ColorDepth

        if self.color_depth in (ColorDepth.TRUECOLOR, ColorDepth.EXTENDED_256):
            # Use 256-color mode: 38;5;N or 48;5;N
            prefix = "38" if foreground else "48"
            return f"{prefix};5;{color_idx}"

        elif self.color_depth == ColorDepth.BASIC_16:
            # Map 256-color to 16-color (simplified mapping)
            if color_idx < 16:
                # Already in basic range
                code = 30 + (color_idx % 8)
                if color_idx >= 8:
                    code += 60  # Bright variant
                if not foreground:
                    code += 10
                return str(code)
            else:
                # Map higher colors to closest basic color
                # This is a simplified mapping; for better results,
                # convert to RGB first then to 16-color
                basic_idx = color_idx % 16
                code = 30 + (basic_idx % 8)
                if basic_idx >= 8:
                    code += 60
                if not foreground:
                    code += 10
                return str(code)

        return ""

    def _encode_named(self, color_name: str, foreground: bool) -> str:
        """Encode named color.

        Args:
            color_name: Color name (e.g., "red", "bright_cyan")
            foreground: True for foreground, False for background

        Returns:
            ANSI color code string
        """
        color_name = color_name.lower()

        # Look up in basic colors map
        if foreground:
            code = BASIC_COLORS.get(color_name)
        else:
            code = BASIC_BG_COLORS.get(color_name)

        if code is not None:
            return str(code)

        return ""
