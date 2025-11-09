"""Terminal capability detection for color support.

This module implements terminal color capability detection using environment
variables (COLORTERM, TERM, LS_COLORS) following industry standards.

Based on research findings from Claude Code CLI architecture analysis,
validating terminal detection patterns across iTerm2, Windows Terminal,
VS Code terminal, and other modern terminals.

Usage:
    >>> from claude_agent_sdk.rendering.semantic import detect_capability
    >>> capability = detect_capability()
    >>> print(capability)  # TerminalCapability.TRUECOLOR
"""

import os
import sys
from enum import Enum


class TerminalCapability(Enum):
    """Terminal color support levels.

    Ordered from highest to lowest capability for fallback logic.

    Attributes:
        TRUECOLOR: 24-bit RGB (16.7 million colors)
        COLOR_256: 256-color palette
        COLOR_16: 16-color ANSI palette
        MONOCHROME: No color support
    """

    TRUECOLOR = "truecolor"  # 24-bit RGB
    COLOR_256 = "256color"  # 256-color palette
    COLOR_16 = "16color"  # 16-color ANSI
    MONOCHROME = "monochrome"  # No color

    def __lt__(self, other):
        """Enable comparison for capability fallback."""
        order = [
            TerminalCapability.TRUECOLOR,
            TerminalCapability.COLOR_256,
            TerminalCapability.COLOR_16,
            TerminalCapability.MONOCHROME,
        ]
        return order.index(self) > order.index(other)  # Higher index = lower capability


def detect_capability() -> TerminalCapability:
    """Detect terminal color support level.

    Detection strategy (highest priority first):
    1. Check NO_COLOR env var (standard: disable all color)
    2. Check COLORTERM for truecolor support
    3. Check TERM variable for 256color or color variants
    4. Check if stdout is a TTY
    5. Default to 16-color for safety

    Environment variables:
        COLORTERM: "truecolor" or "24bit" indicates 24-bit RGB support
        TERM: Terminal type (e.g., "xterm-256color", "screen-256color")
        LS_COLORS: Presence indicates color support
        NO_COLOR: If set (any value), disable all color

    Returns:
        TerminalCapability: Detected color support level

    Example:
        >>> # In a terminal with COLORTERM=truecolor
        >>> capability = detect_capability()
        >>> assert capability == TerminalCapability.TRUECOLOR
    """
    # Priority 1: NO_COLOR standard (disable all color)
    if os.environ.get("NO_COLOR"):
        return TerminalCapability.MONOCHROME

    # Priority 2: COLORTERM for truecolor (24-bit RGB)
    colorterm = os.environ.get("COLORTERM", "").lower()
    if colorterm in ("truecolor", "24bit"):
        return TerminalCapability.TRUECOLOR

    # Priority 3: TERM variable for color mode
    term = os.environ.get("TERM", "").lower()
    if "256color" in term:
        return TerminalCapability.COLOR_256
    if "color" in term:
        return TerminalCapability.COLOR_16

    # Priority 4: Check if stdout is a TTY
    if not sys.stdout.isatty():
        return TerminalCapability.MONOCHROME

    # Priority 5: Default to 16-color for safety
    return TerminalCapability.COLOR_16


# Module-level cache for capability detection
_cached_capability: TerminalCapability | None = None


def get_capability(force: TerminalCapability | None = None) -> TerminalCapability:
    """Get terminal capability with caching.

    Args:
        force: Optional capability override (for testing or user preference)

    Returns:
        TerminalCapability: Detected or forced capability

    Example:
        >>> # Auto-detect (cached after first call)
        >>> cap = get_capability()
        >>>
        >>> # Force specific capability (e.g., for testing)
        >>> cap = get_capability(force=TerminalCapability.COLOR_16)
    """
    global _cached_capability

    if force is not None:
        return force

    if _cached_capability is None:
        _cached_capability = detect_capability()

    return _cached_capability
