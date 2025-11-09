"""Syntax highlighting module for Claude Agent SDK.

This module provides comprehensive syntax highlighting for 500+ programming
languages using a modular, extensible architecture.

Architecture:
    - LanguageRegistry: Language catalog and detection
    - TokenMapper: Pygments token → semantic category mapping
    - SemanticMapping: Semantic category → theme color mapping
    - StructuredDataFormatter: Type-aware JSON/YAML formatting
    - SyntaxHighlighter: Orchestrator coordinating all components

Quick Start:
    >>> from claude_agent_sdk.rendering.theme import Theme
    >>> from claude_agent_sdk.rendering.syntax import SyntaxHighlighter
    >>>
    >>> theme = Theme.claude_code_default()
    >>> highlighter = SyntaxHighlighter(theme)
    >>>
    >>> code = 'def hello(): print("world")'
    >>> highlighted = highlighter.highlight(code, language_hint="python")

Customization:
    >>> from claude_agent_sdk.rendering.syntax import SemanticMapping
    >>>
    >>> # Customize comment coloring
    >>> custom_mapping = SemanticMapping.claude_default().customize({
    ...     "comment": "metadata"  # Dim instead of green
    ... })
    >>> highlighter = SyntaxHighlighter(theme, semantic_mapping=custom_mapping)
"""

from .highlighter import SyntaxHighlighter
from .language_registry import LanguageRegistry, LanguageSpec
from .semantic_mapping import SemanticMapping
from .structured_formatter import StructuredDataFormatter
from .token_mapper import TokenMapper

__all__ = [
    "LanguageRegistry",
    "LanguageSpec",
    "TokenMapper",
    "SemanticMapping",
    "StructuredDataFormatter",
    "SyntaxHighlighter",
]
