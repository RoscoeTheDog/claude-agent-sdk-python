"""Syntax highlighter orchestrator.

This module ties together all syntax highlighting components:
- Language detection (LanguageRegistry)
- Token mapping (TokenMapper)
- Semantic mapping (SemanticMapping)
- Structured formatting (StructuredDataFormatter)

Usage:
    >>> from claude_agent_sdk.rendering.theme import Theme
    >>> from claude_agent_sdk.rendering.syntax import SyntaxHighlighter
    >>>
    >>> theme = Theme.claude_code_default()
    >>> highlighter = SyntaxHighlighter(theme)
    >>>
    >>> # Highlight Python code
    >>> code = 'def hello(): print("world")'
    >>> highlighted = highlighter.highlight(code, language_hint="python")
"""

import importlib.util

from .language_registry import LanguageRegistry, LanguageSpec
from .semantic_mapping import SemanticMapping
from .structured_formatter import StructuredDataFormatter
from .token_mapper import TokenMapper


class SyntaxHighlighter:
    """Orchestrates syntax highlighting for all languages.

    This class coordinates the highlighting pipeline:
    1. Detect language from hint or content
    2. Route to appropriate formatter (semantic or Pygments)
    3. Apply token/type-based coloring
    4. Return ANSI-styled code

    Attributes:
        theme: Theme instance
        semantic_mapping: Semantic category to theme mapping
        enabled: Whether highlighting is enabled
        token_mapper: Pygments token mapper
    """

    def __init__(
        self,
        theme: 'Theme',
        semantic_mapping: SemanticMapping | None = None,
        enabled: bool = True
    ):
        """Initialize highlighter.

        Args:
            theme: Theme instance
            semantic_mapping: Optional custom mapping (uses Claude default if None)
            enabled: Whether highlighting is enabled
        """
        self.theme = theme
        self.semantic_mapping = semantic_mapping or SemanticMapping.claude_default()
        self.enabled = enabled
        self.token_mapper = TokenMapper()
        self._pygments_available = importlib.util.find_spec("pygments") is not None

        # Initialize structured formatter
        self.structured_formatter = StructuredDataFormatter(
            theme=theme,
            semantic_mapping=self.semantic_mapping
        )

    def highlight(
        self,
        code: str,
        language_hint: str | None = None,
        context: str = "code_block"
    ) -> str:
        """Highlight code using appropriate strategy.

        This is the main entry point for syntax highlighting. It:
        1. Detects the language
        2. Routes to semantic formatter (JSON/YAML) or Pygments (general)
        3. Applies ANSI styling

        Args:
            code: Source code to highlight
            language_hint: Language identifier (e.g., "python", "json")
            context: Rendering context ("code_block" or "tool_result")

        Returns:
            ANSI-styled code string

        Falls back to plain code_block style if:
            - Highlighting disabled
            - Pygments not installed
            - Language not recognized
            - Any error during highlighting

        Example:
            >>> highlighter = SyntaxHighlighter(theme)
            >>> code = 'def hello(): pass'
            >>> highlighted = highlighter.highlight(code, language_hint="python")
        """
        if not self.enabled:
            return self._fallback_format(code)

        # Detect language
        lang_spec = LanguageRegistry.detect(hint=language_hint, content=code)

        # Route to semantic formatter for data formats
        if lang_spec.semantic_formatter:
            return self._highlight_with_semantic_formatter(code, lang_spec)

        # Use Pygments for general-purpose languages
        if self._pygments_available:
            return self._highlight_with_pygments(code, lang_spec)

        # Fallback: no Pygments installed
        return self._fallback_format(code)

    def _highlight_with_semantic_formatter(
        self,
        code: str,
        lang_spec: LanguageSpec
    ) -> str:
        """Highlight using semantic formatter (JSON/YAML).

        Args:
            code: Source code
            lang_spec: Language specification

        Returns:
            Semantically formatted code
        """
        if lang_spec.semantic_formatter == "json":
            return self.structured_formatter.format_json(code)
        elif lang_spec.semantic_formatter == "yaml":
            return self.structured_formatter.format_yaml(code)
        else:
            # Unknown semantic formatter - fallback
            return self._fallback_format(code)

    def _highlight_with_pygments(
        self,
        code: str,
        lang_spec: LanguageSpec
    ) -> str:
        """Highlight using Pygments tokenization.

        Pipeline:
        1. Get Pygments lexer for language
        2. Tokenize code
        3. Map each token to semantic category (TokenMapper)
        4. Map semantic category to theme category (SemanticMapping)
        5. Apply ANSI styling from theme

        Args:
            code: Source code
            lang_spec: Language specification

        Returns:
            ANSI-styled code
        """
        try:
            from pygments.lexers import get_lexer_by_name
            from pygments.util import ClassNotFound

            # Get lexer
            try:
                lexer = get_lexer_by_name(lang_spec.pygments_lexer)
            except ClassNotFound:
                return self._fallback_format(code)

            # Tokenize
            tokens = lexer.get_tokens(code)

            # Build styled output
            result = []
            for token_type, value in tokens:
                # Step 1: Pygments token → semantic category
                semantic_cat = self.token_mapper.map_token(token_type)

                # Step 2: Semantic category → theme category
                theme_cat = self.semantic_mapping.get_theme_category(semantic_cat)

                # Step 3: Apply ANSI styling
                styled_value = self._apply_ansi_style(value, theme_cat)
                result.append(styled_value)

            return ''.join(result)

        except Exception:
            # Any error - fallback to plain style
            return self._fallback_format(code)

    def _apply_ansi_style(self, text: str, theme_category: str) -> str:
        """Apply ANSI styling from theme category.

        Args:
            text: Text to style
            theme_category: Theme category name (e.g., "tool_use", "error")

        Returns:
            ANSI-styled text
        """
        from claude_agent_sdk.rendering.ansi import AnsiEncoder

        if hasattr(self.theme, theme_category):
            style_rule = getattr(self.theme, theme_category)
            encoder = AnsiEncoder()
            return encoder.encode(text, style_rule)

        # Theme category not found - no styling
        return text

    def _fallback_format(self, code: str) -> str:
        """Apply plain code_block style without syntax highlighting.

        Args:
            code: Source code

        Returns:
            Code styled with theme.code_block
        """
        return self._apply_ansi_style(code, "code_block")
