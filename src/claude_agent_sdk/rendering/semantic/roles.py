"""Semantic role taxonomy for UI element classification.

This module defines the semantic roles used for classifying UI messages
in the renderer pipeline. Semantic roles enable consistent coloring and
formatting across different message types.

Based on research findings from Claude Code CLI architecture analysis
(19 queries, 66 sources). Follows Sprint 1.5's modular architecture pattern.

Usage:
    >>> from claude_agent_sdk.rendering.semantic import SemanticRole
    >>> role = SemanticRole.ERROR
    >>> role.description
    'Error messages and failures'
"""

from enum import Enum


class SemanticRole(Enum):
    """Semantic classification for UI messages.

    Each role represents a distinct UI context that determines the
    visual presentation (color, icons, formatting) of the message.

    Roles are detected via pattern matching (Story 4.5) and mapped
    to visual styles via UIElementFormatter (Story 4.6).

    Attributes:
        SYSTEM: System status and informational messages
        USER: User input, commands, and requests
        ASSISTANT: LLM-generated responses and content
        TOOL: Tool calls, tool results, and tool activity
        ERROR: Error messages, failures, and exceptions
        WARNING: Warnings, cautions, and potential issues
        SUCCESS: Success indicators and positive confirmations
        INFO: Neutral informational content
        CODE: Code blocks and syntax-highlighted content
        INTERACTIVE: Interactive elements (menus, prompts, selections)
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    INFO = "info"
    CODE = "code"
    INTERACTIVE = "interactive"

    @property
    def description(self) -> str:
        """Human-readable description of this role's purpose."""
        descriptions = {
            SemanticRole.SYSTEM: "System status and informational messages",
            SemanticRole.USER: "User input, commands, and requests",
            SemanticRole.ASSISTANT: "LLM-generated responses and content",
            SemanticRole.TOOL: "Tool calls, tool results, and tool activity",
            SemanticRole.ERROR: "Error messages, failures, and exceptions",
            SemanticRole.WARNING: "Warnings, cautions, and potential issues",
            SemanticRole.SUCCESS: "Success indicators and positive confirmations",
            SemanticRole.INFO: "Neutral informational content",
            SemanticRole.CODE: "Code blocks and syntax-highlighted content",
            SemanticRole.INTERACTIVE: "Interactive elements (menus, prompts, selections)",
        }
        return descriptions[self]

    @property
    def default_icon(self) -> str:
        """Default Unicode icon for this role (from research findings)."""
        icons = {
            SemanticRole.ERROR: "✗",
            SemanticRole.WARNING: "⚠️",
            SemanticRole.SUCCESS: "✓",
            SemanticRole.INFO: "ℹ️",
            SemanticRole.TOOL: "⟳",  # Running/activity indicator
            SemanticRole.INTERACTIVE: "⊙",  # Pending/selection indicator
        }
        return icons.get(self, "")

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"SemanticRole.{self.name}"
