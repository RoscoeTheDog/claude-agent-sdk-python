"""Role detection interface and pattern-based implementation.

This module implements the semantic role detection logic using pattern
matching on message type, content, and metadata. Follows the renderer-side
processing architecture validated by Claude Code CLI research.

Based on research findings:
- Message type detection (tool_use, tool_result, error)
- Content pattern detection (^⚠️, ^✓, etc.)
- Metadata.ui.role support for explicit hints
- Fallback to default role for unknown patterns

Usage:
    >>> from claude_agent_sdk.rendering.semantic import PatternBasedDetector
    >>> detector = PatternBasedDetector()
    >>> role = detector.detect(message)
    >>> print(role)  # SemanticRole.ERROR
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from re import Pattern
from typing import Any

from .roles import SemanticRole


@dataclass
class RoleDetectionConfig:
    """Configuration for semantic role detection.

    Attributes:
        enable_type_detection: Detect roles from message.type field
        enable_content_patterns: Detect roles from content regex patterns
        enable_metadata_hints: Detect roles from message.metadata.ui.role
        default_role: Fallback role when no patterns match
        custom_patterns: Custom regex patterns (role_name -> pattern)
        pattern_priority: Order of detection methods (metadata > type > content)
    """

    enable_type_detection: bool = True
    enable_content_patterns: bool = True
    enable_metadata_hints: bool = True
    default_role: SemanticRole = SemanticRole.ASSISTANT
    custom_patterns: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Compile custom patterns to regex objects."""
        self._compiled_patterns: dict[SemanticRole, Pattern] = {}
        for role_name, pattern_str in self.custom_patterns.items():
            try:
                role = SemanticRole[role_name.upper()]
                self._compiled_patterns[role] = re.compile(pattern_str)
            except (KeyError, re.error):
                pass  # Invalid role or pattern - skip


class RoleDetector(ABC):
    """Abstract base class for semantic role detection.

    Subclasses implement the detect() method to classify messages
    into semantic roles based on message type, content, and metadata.
    """

    @abstractmethod
    def detect(self, message: Any) -> SemanticRole:
        """Detect the semantic role for a message.

        Args:
            message: Message object with type, content, and metadata fields

        Returns:
            SemanticRole: The detected semantic role

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError


class PatternBasedDetector(RoleDetector):
    """Pattern-based semantic role detection.

    Implements the Claude Code CLI renderer-side detection strategy:
    1. Check metadata.ui.role for explicit hints (highest priority)
    2. Check message.type for structural classification
    3. Check content patterns (regex) for visual indicators
    4. Fallback to default role

    Research-validated patterns:
    - Error: message.type == "error"
    - Tool: message.type in ("tool_use", "tool_result")
    - Warning: content starts with ⚠️
    - Success: content starts with ✓
    - Interactive: content contains menu/selection patterns

    Usage:
        >>> detector = PatternBasedDetector()
        >>> role = detector.detect(error_message)
        >>> assert role == SemanticRole.ERROR
    """

    def __init__(self, config: RoleDetectionConfig | None = None):
        """Initialize detector with optional configuration.

        Args:
            config: Configuration for detection behavior. Uses defaults if None.
        """
        self.config = config or RoleDetectionConfig()
        self._build_pattern_registry()

    def _build_pattern_registry(self) -> None:
        """Build compiled regex patterns for content detection.

        Patterns based on research findings from Claude Code CLI:
        - Warning: ^⚠️
        - Success: ^✓
        - Error: ^✗
        - Info: Common info patterns
        """
        self._content_patterns: dict[SemanticRole, Pattern] = {
            SemanticRole.WARNING: re.compile(r"^⚠️"),
            SemanticRole.SUCCESS: re.compile(r"^✓"),
            SemanticRole.ERROR: re.compile(r"^✗"),
            SemanticRole.INFO: re.compile(r"^(ℹ️|Note:|Info:)"),
        }

        # Add custom patterns from config
        if hasattr(self.config, "_compiled_patterns"):
            self._content_patterns.update(self.config._compiled_patterns)

    def detect(self, message: Any) -> SemanticRole:
        """Detect semantic role using multi-tier pattern matching.

        Detection priority (highest to lowest):
        1. Metadata hints (message.metadata.ui.role)
        2. Message type (message.type == "error", "tool_use", etc.)
        3. Content patterns (regex matching on message.content)
        4. Default fallback

        Args:
            message: Message object with type, content, metadata

        Returns:
            SemanticRole: Detected semantic role

        Example:
            >>> msg = Message(type="error", content="Failed to execute")
            >>> role = detector.detect(msg)
            >>> assert role == SemanticRole.ERROR
        """
        # Priority 1: Metadata hints (explicit role override)
        if self.config.enable_metadata_hints:
            role = self._detect_from_metadata(message)
            if role:
                return role

        # Priority 2: Message type detection
        if self.config.enable_type_detection:
            role = self._detect_from_type(message)
            if role:
                return role

        # Priority 3: Content pattern detection
        if self.config.enable_content_patterns:
            role = self._detect_from_content(message)
            if role:
                return role

        # Priority 4: Default fallback
        return self.config.default_role

    def _detect_from_metadata(self, message: Any) -> SemanticRole | None:
        """Detect role from message.metadata.ui.role field.

        Args:
            message: Message object

        Returns:
            SemanticRole if metadata hint present, None otherwise
        """
        try:
            metadata = getattr(message, "metadata", None)
            if metadata:
                ui_metadata = getattr(metadata, "ui", None) or metadata.get("ui")
                if ui_metadata:
                    role_hint = getattr(ui_metadata, "role", None) or ui_metadata.get("role")
                    if role_hint:
                        # Convert string to enum
                        return SemanticRole(role_hint)
        except (AttributeError, KeyError, ValueError):
            pass
        return None

    def _detect_from_type(self, message: Any) -> SemanticRole | None:
        """Detect role from message.type field.

        Type mappings (from research):
        - "error" -> ERROR
        - "tool_use" -> TOOL
        - "tool_result" -> TOOL
        - "system" -> SYSTEM
        - "user" -> USER

        Args:
            message: Message object

        Returns:
            SemanticRole if type matches known pattern, None otherwise
        """
        try:
            msg_type = getattr(message, "type", None)
            if msg_type == "error":
                return SemanticRole.ERROR
            elif msg_type in ("tool_use", "tool_result"):
                return SemanticRole.TOOL
            elif msg_type == "system":
                return SemanticRole.SYSTEM
            elif msg_type == "user":
                return SemanticRole.USER
        except AttributeError:
            pass
        return None

    def _detect_from_content(self, message: Any) -> SemanticRole | None:
        """Detect role from content patterns (regex matching).

        Patterns:
        - ^⚠️ -> WARNING
        - ^✓ -> SUCCESS
        - ^✗ -> ERROR
        - ^(ℹ️|Note:|Info:) -> INFO

        Args:
            message: Message object

        Returns:
            SemanticRole if content matches pattern, None otherwise
        """
        try:
            content = getattr(message, "content", "")
            if isinstance(content, str):
                for role, pattern in self._content_patterns.items():
                    if pattern.match(content):
                        return role
        except AttributeError:
            pass
        return None
