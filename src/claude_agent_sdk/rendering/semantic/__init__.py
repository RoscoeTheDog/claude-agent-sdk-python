"""Semantic role classification for UI messages.

This package implements semantic role taxonomy and detection for
renderer-level UI coloring. Part of Sprint 1.5 Phase 2 architecture.

Modules:
    roles: SemanticRole enum and taxonomy
    role_detector: RoleDetector interface and pattern-based implementation

Usage:
    >>> from claude_agent_sdk.rendering.semantic import (
    ...     SemanticRole,
    ...     PatternBasedDetector,
    ...     RoleDetectionConfig,
    ... )
    >>>
    >>> detector = PatternBasedDetector()
    >>> role = detector.detect(message)
    >>> print(role.description)
"""

from .role_detector import (
    PatternBasedDetector,
    RoleDetectionConfig,
    RoleDetector,
)
from .roles import SemanticRole

__all__ = [
    "SemanticRole",
    "RoleDetector",
    "PatternBasedDetector",
    "RoleDetectionConfig",
]
