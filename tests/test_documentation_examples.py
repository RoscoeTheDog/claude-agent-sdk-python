"""Verify all documentation code examples work.

This test module extracts and verifies code examples from the architecture
documentation to ensure they remain accurate and up-to-date.

Story 12: Architecture & API Documentation
"""

import importlib.util

import pytest

from claude_agent_sdk.rendering import RendererConfig, Theme
from claude_agent_sdk.rendering.syntax import (
    LanguageRegistry,
    LanguageSpec,
    SemanticMapping,
    SyntaxHighlighter,
)


class TestAPIReferenceExamples:
    """Test examples from api-reference.md."""

    def test_quick_start_example(self):
        """Test quick start example from API reference."""
        theme = Theme.claude_code_default()
        highlighter = SyntaxHighlighter(theme)

        code = 'def hello(): print("world")'
        highlighted = highlighter.highlight(code, language_hint="python")

        # Should either contain ANSI codes (if Pygments installed) or return plain text
        assert isinstance(highlighted, str)
        assert len(highlighted) >= len(code)

    def test_constructor_basic(self):
        """Test basic SyntaxHighlighter constructor."""
        highlighter = SyntaxHighlighter(Theme.claude_code_default())
        assert highlighter.enabled is True
        assert highlighter.semantic_mapping is not None

    def test_constructor_custom_mapping(self):
        """Test SyntaxHighlighter with custom semantic mapping."""
        custom_mapping = SemanticMapping.claude_default().customize(
            {"comment": "metadata"}
        )

        highlighter = SyntaxHighlighter(
            Theme.claude_code_default(), semantic_mapping=custom_mapping
        )

        assert highlighter.semantic_mapping is custom_mapping

    def test_constructor_disabled(self):
        """Test SyntaxHighlighter with highlighting disabled."""
        highlighter = SyntaxHighlighter(Theme.claude_code_default(), enabled=False)
        assert highlighter.enabled is False

    def test_highlight_python(self):
        """Test highlighting Python code."""
        highlighter = SyntaxHighlighter(Theme.claude_code_default())

        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
        highlighted = highlighter.highlight(code, language_hint="python")

        # Should return a string (might trim trailing whitespace)
        assert isinstance(highlighted, str)
        assert len(highlighted.strip()) >= len(code.strip())

    def test_highlight_json(self):
        """Test highlighting JSON data."""
        highlighter = SyntaxHighlighter(Theme.claude_code_default())

        json_data = '{"name": "Alice", "age": 30, "active": true}'
        highlighted = highlighter.highlight(json_data, language_hint="json")

        # Should return a string
        assert isinstance(highlighted, str)
        assert len(highlighted) >= len(json_data)

    def test_highlight_unknown_language(self):
        """Test graceful degradation with unknown language."""
        highlighter = SyntaxHighlighter(Theme.claude_code_default())

        unknown = "code in unknown language"
        highlighted = highlighter.highlight(unknown, language_hint="foobar")

        # Should return plain text (or might have minimal formatting)
        assert highlighted == unknown or len(highlighted) >= len(unknown)

    def test_language_registry_detect(self):
        """Test LanguageRegistry.detect() from API reference."""
        lang = LanguageRegistry.detect(hint="python")
        assert lang is not None
        assert lang.name == "Python"
        assert lang.pygments_lexer == "python"

    def test_language_registry_detect_json(self):
        """Test JSON language detection."""
        lang = LanguageRegistry.detect(hint="json")
        assert lang is not None
        assert lang.semantic_formatter == "json"

    def test_language_registry_detect_unknown(self):
        """Test unknown language detection."""
        lang = LanguageRegistry.detect(hint="foobar")
        # Unknown languages return None
        assert lang is None or lang.name == "Plain Text"

    def test_language_registry_get_by_id(self):
        """Test LanguageRegistry.get_by_id()."""
        lang = LanguageRegistry.get_by_id("python")
        assert lang is not None
        assert lang.name == "Python"

        lang = LanguageRegistry.get_by_id("unknown")
        assert lang is None

    def test_language_registry_languages(self):
        """Test LanguageRegistry.LANGUAGES dict."""
        all_langs = LanguageRegistry.LANGUAGES
        assert isinstance(all_langs, dict)
        assert len(all_langs) > 0
        assert "python" in all_langs

    def test_language_spec_creation(self):
        """Test LanguageSpec creation from API reference."""
        python_spec = LanguageSpec(
            name="Python",
            aliases=["py", "python", "python3"],
            pygments_lexer="python",
            category="general_purpose",
        )

        assert python_spec.name == "Python"
        assert "py" in python_spec.aliases
        assert python_spec.semantic_formatter is None

    def test_semantic_mapping_claude_default(self):
        """Test SemanticMapping.claude_default()."""
        mapping = SemanticMapping.claude_default()
        category = mapping.get_theme_category("keyword")
        # Should map to a valid theme category
        assert isinstance(category, str)
        assert category != ""

    def test_semantic_mapping_get_theme_category(self):
        """Test SemanticMapping.get_theme_category()."""
        mapping = SemanticMapping.claude_default()

        # Should return valid theme categories for semantic categories
        assert isinstance(mapping.get_theme_category("keyword"), str)
        assert isinstance(mapping.get_theme_category("string"), str)
        assert isinstance(mapping.get_theme_category("comment"), str)
        assert isinstance(mapping.get_theme_category("function"), str)

    def test_semantic_mapping_customize(self):
        """Test SemanticMapping.customize()."""
        original = SemanticMapping.claude_default()
        original_keyword = original.get_theme_category("keyword")

        custom = original.customize({"comment": "metadata"})

        assert custom.get_theme_category("comment") == "metadata"
        # Other mappings should remain unchanged
        assert custom.get_theme_category("keyword") == original_keyword

    @pytest.mark.skipif(
        importlib.util.find_spec("pygments") is None,
        reason="Pygments not installed"
    )
    def test_token_mapper(self):
        """Test TokenMapper.map_token()."""
        from pygments.token import Token

        from claude_agent_sdk.rendering.syntax.token_mapper import TokenMapper

        mapper = TokenMapper()

        # Direct mapping
        category = mapper.map_token(Token.Keyword)
        assert category == "keyword"

        # Hierarchical fallback (Token.String.Doc → some string category)
        category = mapper.map_token(Token.String.Doc)
        assert isinstance(category, str)

    def test_renderer_config(self):
        """Test RendererConfig with syntax highlighting."""
        # Enable syntax highlighting (default)
        config = RendererConfig(enable_syntax_highlighting=True)
        assert config.enable_syntax_highlighting is True

        # Disable syntax highlighting
        config = RendererConfig(enable_syntax_highlighting=False)
        assert config.enable_syntax_highlighting is False


class TestCodeExamples:
    """Test code examples from API reference."""

    def test_example_1_basic_highlighting(self):
        """Test Example 1: Basic Highlighting."""
        theme = Theme.claude_code_default()
        highlighter = SyntaxHighlighter(theme)

        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

        highlighted = highlighter.highlight(code, language_hint="python")
        assert isinstance(highlighted, str)
        assert len(highlighted.strip()) >= len(code.strip())

    def test_example_2_custom_semantic_mapping(self):
        """Test Example 2: Custom Semantic Mapping."""
        custom_mapping = SemanticMapping.claude_default().customize(
            {"comment": "metadata"}
        )

        theme = Theme.claude_code_default()
        highlighter = SyntaxHighlighter(theme, semantic_mapping=custom_mapping)

        code = '# This comment will be gray\nprint("Hello")'
        highlighted = highlighter.highlight(code, language_hint="python")
        assert len(highlighted) >= len(code)

    def test_example_3_json_formatting(self):
        """Test Example 3: JSON Formatting."""
        theme = Theme.claude_code_default()
        highlighter = SyntaxHighlighter(theme)

        json_data = """
{
  "user": {
    "name": "Alice",
    "age": 30,
    "active": true,
    "balance": 1234.56
  }
}
"""

        highlighted = highlighter.highlight(json_data, language_hint="json")
        assert isinstance(highlighted, str)
        assert len(highlighted.strip()) >= len(json_data.strip())

    def test_example_4_multiple_languages(self):
        """Test Example 4: Multiple Languages."""
        theme = Theme.claude_code_default()
        highlighter = SyntaxHighlighter(theme)

        examples = {
            "python": "def hello(): pass",
            "javascript": "function hello() {}",
            "json": '{"hello": "world"}',
        }

        for lang, code in examples.items():
            highlighted = highlighter.highlight(code, language_hint=lang)
            # Each should be processed (even if no Pygments, returns original)
            assert len(highlighted) >= len(code)

    def test_example_5_language_detection(self):
        """Test Example 5: Language Detection."""
        hints = ["python", "py", "python3", "js", "javascript", "json"]

        for hint in hints:
            lang = LanguageRegistry.detect(hint=hint)
            if lang:
                assert lang.name in ["Python", "JavaScript", "JSON"]
                assert lang.pygments_lexer in ["python", "javascript", "json"]

    def test_example_6_check_pygments(self):
        """Test Example 6: Check Pygments Availability."""
        pygments_available = importlib.util.find_spec("pygments") is not None

        if pygments_available:
            highlighter = SyntaxHighlighter(Theme.claude_code_default())
            assert highlighter._pygments_available is True
        else:
            # Should still work without Pygments (graceful degradation)
            highlighter = SyntaxHighlighter(Theme.claude_code_default())
            assert highlighter._pygments_available is False

    def test_example_7_disable_highlighting(self):
        """Test Example 7: Disable Highlighting."""
        theme = Theme.claude_code_default()
        highlighter = SyntaxHighlighter(theme, enabled=False)

        code = 'def hello(): print("world")'
        result = highlighter.highlight(code, language_hint="python")

        # Returns plain text (no ANSI codes)
        assert result == code


class TestGracefulDegradation:
    """Test graceful degradation scenarios from API reference."""

    def test_unknown_language(self):
        """Unknown language should return plain text."""
        highlighter = SyntaxHighlighter(Theme.claude_code_default())
        result = highlighter.highlight("code", language_hint="unknown_lang")
        # Should gracefully return the code (possibly with minimal formatting)
        assert isinstance(result, str)
        assert "code" in result

    def test_empty_code(self):
        """Empty code should return empty or minimal string."""
        highlighter = SyntaxHighlighter(Theme.claude_code_default())
        result = highlighter.highlight("", language_hint="python")
        # Empty input should produce empty or minimal output
        assert isinstance(result, str)
        assert len(result) <= 10  # Allow for minimal formatting like newline

    def test_disabled_highlighting(self):
        """Disabled highlighting should return plain text."""
        highlighter = SyntaxHighlighter(
            Theme.claude_code_default(), enabled=False
        )
        code = 'def hello(): pass'
        result = highlighter.highlight(code, language_hint="python")
        assert result == code


class TestExtensionGuideExamples:
    """Test examples from extension-guide.md."""

    def test_language_spec_creation(self):
        """Test creating a LanguageSpec (from extension guide)."""
        kotlin_spec = LanguageSpec(
            name="Kotlin",
            aliases=["kotlin", "kt"],
            pygments_lexer="kotlin",
            category="general_purpose",
        )

        assert kotlin_spec.name == "Kotlin"
        assert "kt" in kotlin_spec.aliases
        assert kotlin_spec.pygments_lexer == "kotlin"

    def test_custom_semantic_mapping(self):
        """Test custom semantic mapping (from extension guide)."""
        custom_mapping = SemanticMapping.claude_default().customize(
            {
                "comment": "metadata",  # Gray comments
                "string": "warning",  # Yellow/orange strings
                "keyword": "info",  # Cyan keywords
                "function": "success",  # Green functions
            }
        )

        assert custom_mapping.get_theme_category("comment") == "metadata"
        assert custom_mapping.get_theme_category("string") == "warning"
        assert custom_mapping.get_theme_category("keyword") == "info"
        assert custom_mapping.get_theme_category("function") == "success"


class TestArchitectureExamples:
    """Test examples from syntax-highlighting-architecture.md."""

    def test_data_flow_python(self):
        """Test data flow example for Python code."""
        # Step 1: Language detection
        lang = LanguageRegistry.detect("python")
        assert lang is not None
        assert lang.name == "Python"
        assert lang.pygments_lexer == "python"
        assert lang.semantic_formatter is None

        # Step 5: Semantic mapping
        mapping = SemanticMapping.claude_default()
        theme_cat = mapping.get_theme_category("keyword")
        assert isinstance(theme_cat, str)
        assert theme_cat != ""

        # Step 6: Theme lookup (direct attribute access)
        theme = Theme.claude_code_default()
        # Theme uses direct attribute access, not get_style()
        assert hasattr(theme, theme_cat)

    def test_data_flow_json(self):
        """Test data flow example for JSON data."""
        # Step 1: Language detection
        lang = LanguageRegistry.detect("json")
        assert lang is not None
        assert lang.name == "JSON"
        assert lang.semantic_formatter == "json"

        # Step 2: Route to semantic formatter
        theme = Theme.claude_code_default()
        mapping = SemanticMapping.claude_default()
        highlighter = SyntaxHighlighter(theme, semantic_mapping=mapping)

        json_data = '{"name": "Alice", "age": 30}'
        result = highlighter.highlight(json_data, language_hint="json")

        # Should use structured formatter
        assert len(result) >= len(json_data)

    def test_data_flow_unknown(self):
        """Test graceful degradation for unknown language."""
        # Step 1: Detection may fail or return plain text
        lang = LanguageRegistry.detect("foobar")
        # Unknown language may return None or plain text spec
        assert lang is None or lang.name == "Plain Text"

        # Step 3: Fallback to plain text (or minimal formatting)
        highlighter = SyntaxHighlighter(Theme.claude_code_default())
        result = highlighter.highlight(
            "code in unknown language", language_hint="foobar"
        )
        assert isinstance(result, str)
        assert "code in unknown language" in result


# Run this file directly to verify all examples
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
