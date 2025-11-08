"""Semantic block classifier for theme mapping.

This module provides the BlockClassifier which maps content blocks to semantic
categories for theme-based styling. It uses a three-tier classification system:

1. Type-based classification (authoritative)
2. Tool name classification
3. Content heuristics (fallback)

Example:
    >>> from claude_agent_sdk.types import ToolResultBlock, TextBlock
    >>> classifier = BlockClassifier()
    >>>
    >>> # Type-based classification
    >>> error_block = ToolResultBlock(tool_use_id="123", is_error=True)
    >>> classifier.classify(error_block)  # Returns "tool_error"
    >>>
    >>> # Content heuristics
    >>> text_block = TextBlock(text="Error: Something went wrong")
    >>> classifier.classify(text_block)  # Returns "error"
"""

import re
from typing import Any

from ..types import TextBlock, ThinkingBlock, ToolResultBlock, ToolUseBlock


class BlockClassifier:
    """Maps content blocks to semantic categories for theme application.

    The classifier uses a three-tier system to determine the semantic category:

    Tier 1 (Authoritative): Type-based classification
        - ToolResultBlock.is_error -> "tool_error"
        - ToolResultBlock (success) -> "tool_result"
        - ToolUseBlock -> classify by tool name (Tier 2)
        - ThinkingBlock -> "thinking"

    Tier 2 (Tool Categories): Classify by tool name
        - File operations: "Read", "Write", "Edit", "Glob", "NotebookEdit"
        - Commands: "Bash", "KillShell", "BashOutput"
        - Search: "Grep", "WebSearch", "WebFetch"
        - Questions: "AskUserQuestion"
        - Tasks: "Task"

    Tier 3 (Content Heuristics): Pattern matching on text content
        - Error patterns: "error:", "ERROR", "❌", "failed", etc.
        - Warning patterns: "warning:", "WARNING", "⚠️", etc.
        - Success patterns: "success:", "✅", "completed", etc.
        - Info patterns: "info:", "ℹ️", etc.

    Attributes:
        None (stateless classifier)

    Example:
        >>> classifier = BlockClassifier()
        >>>
        >>> # Classify tool error
        >>> error_block = ToolResultBlock(tool_use_id="1", is_error=True)
        >>> classifier.classify(error_block)
        'tool_error'
        >>>
        >>> # Classify file operation
        >>> read_tool = ToolUseBlock(id="2", name="Read", input={})
        >>> classifier.classify(read_tool)
        'tool_use'
        >>>
        >>> # Classify by content heuristics
        >>> error_text = TextBlock(text="Error: File not found")
        >>> classifier.classify(error_text)
        'error'
    """

    # Tier 3: Content pattern mappings
    _ERROR_PATTERNS = [
        r"^error:",
        r"^ERROR",
        r"^❌",
        r"\bfailed\b",
        r"\bFAILED\b",
        r"\bfatal\b",
        r"\bFATAL\b",
        r"\w+Error:",
        r"\w+Exception:",
        r"Traceback",
        r"not found",
        r"cannot",
        r"unable to",
    ]

    _WARNING_PATTERNS = [
        r"^warning:",
        r"^WARNING",
        r"^⚠️",
        r"^warn:",
        r"^WARN",
        r"\bdeprecated\b",
        r"\bDEPRECATED\b",
    ]

    _SUCCESS_PATTERNS = [
        r"^success:",
        r"^SUCCESS",
        r"^✅",
        r"\bcompleted\b",
        r"\bCOMPLETED\b",
        r"\bdone\b",
        r"\bDONE\b",
        r"\bpassed\b",
        r"\bPASSED\b",
    ]

    _INFO_PATTERNS = [
        r"^info:",
        r"^INFO",
        r"^ℹ️",
        r"^note:",
        r"^NOTE",
    ]

    def __init__(self) -> None:
        """Initialize the block classifier."""
        # Compile regex patterns for efficiency
        self._error_regex = re.compile(
            "|".join(f"({p})" for p in self._ERROR_PATTERNS),
            re.MULTILINE | re.IGNORECASE,
        )
        self._warning_regex = re.compile(
            "|".join(f"({p})" for p in self._WARNING_PATTERNS),
            re.MULTILINE | re.IGNORECASE,
        )
        self._success_regex = re.compile(
            "|".join(f"({p})" for p in self._SUCCESS_PATTERNS),
            re.MULTILINE | re.IGNORECASE,
        )
        self._info_regex = re.compile(
            "|".join(f"({p})" for p in self._INFO_PATTERNS),
            re.MULTILINE | re.IGNORECASE,
        )

    def classify(self, block: Any) -> str:
        """Classify a content block into a semantic category.

        Uses a three-tier classification system to determine the appropriate
        semantic category for theme application.

        Args:
            block: Content block to classify (TextBlock, ToolUseBlock,
                   ToolResultBlock, ThinkingBlock, or other)

        Returns:
            Semantic category name as string. Returns "text" as fallback.

        Example:
            >>> classifier = BlockClassifier()
            >>> block = ToolResultBlock(tool_use_id="1", is_error=True)
            >>> classifier.classify(block)
            'tool_error'
        """
        # Tier 1: Type-based classification (authoritative)
        if isinstance(block, ToolResultBlock):
            if block.is_error:
                return "tool_error"
            return "tool_result"

        if isinstance(block, ToolUseBlock):
            # All tool uses get the same category regardless of tool name
            return "tool_use"

        if isinstance(block, ThinkingBlock):
            return "thinking"

        # Tier 3: Content heuristics for TextBlock
        if isinstance(block, TextBlock):
            return self._classify_text_content(block.text)

        # Fallback: default text styling
        return "text"

    def _classify_text_content(self, text: str) -> str:
        """Classify text content using heuristic pattern matching.

        Args:
            text: Text content to classify

        Returns:
            Semantic category: "error", "warning", "success", "info", or "text"
        """
        if not text:
            return "text"

        # Trim text for pattern matching
        text_stripped = text.strip()

        # Check patterns in priority order
        if self._error_regex.search(text_stripped):
            return "error"

        if self._warning_regex.search(text_stripped):
            return "warning"

        if self._success_regex.search(text_stripped):
            return "success"

        if self._info_regex.search(text_stripped):
            return "info"

        # Default to plain text
        return "text"

    def _matches_error(self, text: str) -> bool:
        """Check if text matches error patterns.

        Args:
            text: Text to check

        Returns:
            True if text matches error patterns
        """
        return bool(self._error_regex.search(text.strip()))

    def _matches_warning(self, text: str) -> bool:
        """Check if text matches warning patterns.

        Args:
            text: Text to check

        Returns:
            True if text matches warning patterns
        """
        return bool(self._warning_regex.search(text.strip()))

    def _matches_success(self, text: str) -> bool:
        """Check if text matches success patterns.

        Args:
            text: Text to check

        Returns:
            True if text matches success patterns
        """
        return bool(self._success_regex.search(text.strip()))

    def _matches_info(self, text: str) -> bool:
        """Check if text matches info patterns.

        Args:
            text: Text to check

        Returns:
            True if text matches info patterns
        """
        return bool(self._info_regex.search(text.strip()))
