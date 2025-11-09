"""Semantic role classification and formatting for UI messages.

This package implements semantic role taxonomy, detection, and ANSI
formatting for renderer-level UI coloring. Part of Sprint 1.5 Phase 2.

Modules:
    roles: SemanticRole enum and taxonomy (Story 4.5)
    role_detector: RoleDetector interface and pattern-based implementation (Story 4.5)
    terminal_capability: Terminal color capability detection (Story 4.6)
    theme: ColorTheme definitions (Story 4.6)
    formatter: UIElementFormatter interface and ANSI implementation (Story 4.6)

Usage:
    >>> from claude_agent_sdk.rendering.semantic import (
    ...     SemanticRole,
    ...     PatternBasedDetector,
    ...     ANSIFormatter,
    ...     default_theme,
    ... )
    >>>
    >>> # Detect role
    >>> detector = PatternBasedDetector()
    >>> role = detector.detect(message)
    >>>
    >>> # Format with color
    >>> formatter = ANSIFormatter()
    >>> formatted = formatter.format(message.content, role)
"""

from .formatter import ANSIFormatter, FormatterConfig, UIElementFormatter
from .role_detector import (
    PatternBasedDetector,
    RoleDetectionConfig,
    RoleDetector,
)
from .roles import SemanticRole
from .terminal_capability import TerminalCapability, detect_capability, get_capability
from .theme import STATUS_ICONS, ColorTheme, default_theme

__all__ = [
    # Story 4.5 exports
    "SemanticRole",
    "RoleDetector",
    "PatternBasedDetector",
    "RoleDetectionConfig",
    # Story 4.6 exports
    "TerminalCapability",
    "detect_capability",
    "get_capability",
    "ColorTheme",
    "default_theme",
    "STATUS_ICONS",
    "UIElementFormatter",
    "ANSIFormatter",
    "FormatterConfig",
]
