# Story 4: Unified Syntax & Semantic Highlighting (v2)

**Status**: unassigned
**Assignee**: unassigned
**Estimated Time**: 4 hours
**Actual Time**: TBD
**Priority**: HIGH
**Version**: 2.0 (Replaces archived Stories 4 & 10)

---

## Dependencies

- Story 1 (COMPLETED) - Provides complete ANSI color mappings from Claude CLI
- Story 2 (unassigned) - Provides accurate theme foundation
- Reference: `.claude/implementation/stories/1-color-analysis.md`

---

## Description

Implement comprehensive syntax highlighting for ALL programming languages using a modular, extensible architecture. This story consolidates code block highlighting and structured data formatting into a unified system that supports 500+ languages via Pygments while maintaining clean separation of concerns.

**Architecture Philosophy**: Separate language detection, syntax tokenization, semantic mapping, and theme application into distinct, composable modules.

**Goal**: Support unlimited languages with customizable theming and zero code duplication between code blocks and tool results.

---

## Acceptance Criteria

### Module 1: Language Registry
- [ ] Create `src/claude_agent_sdk/rendering/syntax/language_registry.py`
- [ ] Implement `LanguageSpec` dataclass with metadata (name, aliases, pygments_lexer, category)
- [ ] Implement `LanguageRegistry` class with 20+ predefined language specs
- [ ] Support language categories: general_purpose, data_format, markup, shell, database
- [ ] Implement language detection from fence hints (e.g., ` ```python `)
- [ ] Support semantic formatter flag for data formats (JSON, YAML)

### Module 2: Token Mapper
- [ ] Create `src/claude_agent_sdk/rendering/syntax/token_mapper.py`
- [ ] Implement `TokenMapper` class with complete Pygments token mapping
- [ ] Map 100+ Pygments token types to semantic categories
- [ ] Implement token hierarchy fallback (walk up parent tokens)
- [ ] Semantic categories: keyword, string_literal, comment, number_literal, type_annotation, etc.

### Module 3: Semantic Mapping
- [ ] Create `src/claude_agent_sdk/rendering/syntax/semantic_mapping.py`
- [ ] Implement `SemanticMapping` class with extensible dict-based mapping
- [ ] Default mapping matches Story 1 findings (keywords→blue, strings→red, etc.)
- [ ] Implement `customize()` method for per-language overrides
- [ ] Support fallback to "default" category for unknown semantic types

### Module 4: Structured Data Formatter
- [ ] Create `src/claude_agent_sdk/rendering/syntax/structured_formatter.py`
- [ ] Implement `StructuredDataFormatter` class for JSON/YAML
- [ ] JSON formatting: keys→dim, string_values→green, numbers→green, booleans→cyan
- [ ] YAML formatting: keys→blue, string_values→red, numbers→green, booleans→cyan
- [ ] Preserve indentation and structure
- [ ] Handle nested objects/arrays recursively

### Module 5: Syntax Highlighter (Orchestrator)
- [ ] Create `src/claude_agent_sdk/rendering/syntax/highlighter.py`
- [ ] Implement `SyntaxHighlighter` orchestrator class
- [ ] Integrate all 4 modules above
- [ ] Auto-detect and route to semantic formatter for data formats
- [ ] Use Pygments pipeline for general-purpose languages
- [ ] Graceful degradation if Pygments not installed
- [ ] Fallback to plain `code_block` theme style

### Integration
- [ ] Add `pygments>=2.17` to `pyproject.toml` optional dependencies
- [ ] Modify `src/claude_agent_sdk/rendering/theme.py` - Add `semantic_mapping` field
- [ ] Modify `src/claude_agent_sdk/rendering/config.py` - Add `enable_syntax_highlighting: bool = True`
- [ ] Modify `src/claude_agent_sdk/rendering/formatters.py` - Integrate `SyntaxHighlighter`
- [ ] Use highlighter for both code blocks AND tool results (unified path)

### Documentation (as you implement)
- [ ] Document each module with docstrings (see Story 12 requirements)
- [ ] Add inline comments for complex token mapping logic
- [ ] Include usage examples in module docstrings

---

## Technical Implementation

### Module 1: Language Registry

**File**: `src/claude_agent_sdk/rendering/syntax/language_registry.py`

```python
"""Language registry for syntax highlighting.

This module maintains the catalog of supported programming languages
and their metadata. New languages can be added by simply adding entries
to the LANGUAGES dict - no code changes required.

Usage:
    >>> lang = LanguageRegistry.detect(hint="python")
    >>> lang.name
    'Python'
    >>> lang.pygments_lexer
    'python'
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class LanguageSpec:
    """Specification for a programming language.

    Attributes:
        name: Human-readable name (e.g., "Python", "JavaScript")
        aliases: List of fence hint aliases (e.g., ["py", "python", "python3"])
        pygments_lexer: Lexer name for Pygments.get_lexer_by_name()
        category: Language category for grouping/filtering
        semantic_formatter: Optional override to use StructuredDataFormatter
                           instead of Pygments (e.g., "json", "yaml")

    Example:
        >>> python_spec = LanguageSpec(
        ...     name="Python",
        ...     aliases=["py", "python", "python3"],
        ...     pygments_lexer="python",
        ...     category="general_purpose"
        ... )
    """

    name: str
    aliases: List[str]
    pygments_lexer: str
    category: str  # general_purpose, data_format, markup, shell, database
    semantic_formatter: Optional[str] = None  # "json", "yaml", or None


class LanguageRegistry:
    """Central registry of supported programming languages.

    This class maintains a catalog of language specifications and provides
    language detection from fence hints (e.g., ```python) or content analysis.

    To add a new language, simply add an entry to the LANGUAGES dict.
    No code changes required.

    Usage:
        >>> # Detect from fence hint
        >>> lang = LanguageRegistry.detect(hint="python")
        >>>
        >>> # Check if uses semantic formatter
        >>> if lang.semantic_formatter:
        ...     # Use StructuredDataFormatter
        ... else:
        ...     # Use Pygments
    """

    # Language catalog - add new languages here
    LANGUAGES: Dict[str, LanguageSpec] = {
        # General Purpose Languages
        "python": LanguageSpec(
            name="Python",
            aliases=["py", "python", "python3"],
            pygments_lexer="python",
            category="general_purpose"
        ),
        "javascript": LanguageSpec(
            name="JavaScript",
            aliases=["js", "javascript"],
            pygments_lexer="javascript",
            category="general_purpose"
        ),
        "typescript": LanguageSpec(
            name="TypeScript",
            aliases=["ts", "typescript"],
            pygments_lexer="typescript",
            category="general_purpose"
        ),
        "java": LanguageSpec(
            name="Java",
            aliases=["java"],
            pygments_lexer="java",
            category="general_purpose"
        ),
        "csharp": LanguageSpec(
            name="C#",
            aliases=["csharp", "cs", "c#"],
            pygments_lexer="csharp",
            category="general_purpose"
        ),
        "ruby": LanguageSpec(
            name="Ruby",
            aliases=["ruby", "rb"],
            pygments_lexer="ruby",
            category="general_purpose"
        ),
        "php": LanguageSpec(
            name="PHP",
            aliases=["php"],
            pygments_lexer="php",
            category="general_purpose"
        ),
        "swift": LanguageSpec(
            name="Swift",
            aliases=["swift"],
            pygments_lexer="swift",
            category="general_purpose"
        ),
        "kotlin": LanguageSpec(
            name="Kotlin",
            aliases=["kotlin", "kt"],
            pygments_lexer="kotlin",
            category="general_purpose"
        ),

        # Systems Programming
        "rust": LanguageSpec(
            name="Rust",
            aliases=["rust", "rs"],
            pygments_lexer="rust",
            category="general_purpose"
        ),
        "go": LanguageSpec(
            name="Go",
            aliases=["go", "golang"],
            pygments_lexer="go",
            category="general_purpose"
        ),
        "c": LanguageSpec(
            name="C",
            aliases=["c"],
            pygments_lexer="c",
            category="general_purpose"
        ),
        "cpp": LanguageSpec(
            name="C++",
            aliases=["cpp", "c++", "cxx"],
            pygments_lexer="cpp",
            category="general_purpose"
        ),

        # Data Formats (use semantic formatters)
        "json": LanguageSpec(
            name="JSON",
            aliases=["json"],
            pygments_lexer="json",
            category="data_format",
            semantic_formatter="json"  # Use StructuredDataFormatter
        ),
        "yaml": LanguageSpec(
            name="YAML",
            aliases=["yaml", "yml"],
            pygments_lexer="yaml",
            category="data_format",
            semantic_formatter="yaml"  # Use StructuredDataFormatter
        ),
        "xml": LanguageSpec(
            name="XML",
            aliases=["xml"],
            pygments_lexer="xml",
            category="data_format"
        ),
        "toml": LanguageSpec(
            name="TOML",
            aliases=["toml"],
            pygments_lexer="toml",
            category="data_format"
        ),

        # Markup Languages
        "html": LanguageSpec(
            name="HTML",
            aliases=["html", "htm"],
            pygments_lexer="html",
            category="markup"
        ),
        "css": LanguageSpec(
            name="CSS",
            aliases=["css"],
            pygments_lexer="css",
            category="markup"
        ),
        "scss": LanguageSpec(
            name="SCSS",
            aliases=["scss", "sass"],
            pygments_lexer="scss",
            category="markup"
        ),
        "markdown": LanguageSpec(
            name="Markdown",
            aliases=["markdown", "md"],
            pygments_lexer="markdown",
            category="markup"
        ),

        # Shell/Scripting
        "bash": LanguageSpec(
            name="Bash",
            aliases=["bash", "sh", "shell"],
            pygments_lexer="bash",
            category="shell"
        ),
        "powershell": LanguageSpec(
            name="PowerShell",
            aliases=["powershell", "ps1"],
            pygments_lexer="powershell",
            category="shell"
        ),

        # Database
        "sql": LanguageSpec(
            name="SQL",
            aliases=["sql", "postgresql", "mysql", "sqlite"],
            pygments_lexer="sql",
            category="database"
        ),

        # Add more languages as needed - 500+ supported by Pygments!
    }

    @classmethod
    def detect(cls, hint: Optional[str] = None, content: Optional[str] = None) -> LanguageSpec:
        """Detect language from fence hint or content analysis.

        Args:
            hint: Language hint from code fence (e.g., "python" from ```python)
            content: Source code content for fallback detection

        Returns:
            LanguageSpec for detected language, or plaintext fallback

        Example:
            >>> lang = LanguageRegistry.detect(hint="py")
            >>> lang.name
            'Python'
        """
        # Try fence hint first
        if hint:
            hint_lower = hint.lower().strip()
            for lang_id, spec in cls.LANGUAGES.items():
                if hint_lower in spec.aliases or hint_lower == lang_id:
                    return spec

        # Fallback: content-based detection (future enhancement)
        # Could use Pygments' guess_lexer(content) here

        # Unknown language - return plaintext
        return cls.get_plaintext()

    @classmethod
    def get_plaintext(cls) -> LanguageSpec:
        """Get fallback spec for unknown/plain text.

        Returns:
            LanguageSpec for plain text (no syntax highlighting)
        """
        return LanguageSpec(
            name="Plain Text",
            aliases=["text", "plaintext", "txt"],
            pygments_lexer="text",
            category="plaintext"
        )

    @classmethod
    def get_by_id(cls, lang_id: str) -> Optional[LanguageSpec]:
        """Get language spec by ID.

        Args:
            lang_id: Language identifier (e.g., "python", "javascript")

        Returns:
            LanguageSpec if found, None otherwise
        """
        return cls.LANGUAGES.get(lang_id.lower())
```

---

### Module 2: Token Mapper

**File**: `src/claude_agent_sdk/rendering/syntax/token_mapper.py`

```python
"""Pygments token to semantic category mapper.

This module maps Pygments token types to language-agnostic semantic
categories. This abstraction layer allows themes to customize syntax
coloring without knowledge of specific Pygments token types.

Token Hierarchy:
    Pygments uses a token hierarchy where specific tokens inherit from
    parent types. For example:
        Token.Name.Function inherits from Token.Name
        Token.Keyword.Type inherits from Token.Keyword

    This mapper uses exact matches first, then walks up the hierarchy
    to find the most specific semantic category.

Usage:
    >>> from pygments.token import Token
    >>> mapper = TokenMapper()
    >>> mapper.map_token(Token.Keyword)
    'keyword'
    >>> mapper.map_token(Token.Name.Function)
    'function_name'
"""

from pygments.token import Token
from typing import Dict


class TokenMapper:
    """Maps Pygments token types to semantic categories.

    This provides a language-agnostic abstraction layer between Pygments
    tokenization and theme styling. Themes can then map semantic categories
    to colors without needing to know about specific Pygments tokens.

    Semantic Categories:
        - keyword: Language keywords (if, def, class, etc.)
        - keyword_operator: Keyword-style operators (and, or, not)
        - string_literal: String values
        - escape_sequence: Escape sequences in strings
        - number_literal: Numeric values
        - boolean_literal: Boolean values (true/false)
        - comment: Comments and documentation
        - doc_string: Docstrings
        - type_annotation: Type hints and annotations
        - class_type: Class names in type context
        - class_name: Class names in definition context
        - function_name: Function/method names
        - builtin_function: Built-in functions (print, len, etc.)
        - decorator: Decorators (@dataclass, etc.)
        - special_identifier: Special names (self, this, cls)
        - identifier: Generic identifiers
        - operator: Operators (+, -, ==, etc.)
        - punctuation: Brackets, commas, etc.
        - default: Fallback for unknown tokens
    """

    # Complete Pygments token → semantic category mapping
    TOKEN_TO_SEMANTIC: Dict[Token, str] = {
        # ===== Keywords =====
        Token.Keyword: "keyword",
        Token.Keyword.Constant: "boolean_literal",  # True, False, true, false
        Token.Keyword.Declaration: "keyword",  # var, let, const
        Token.Keyword.Namespace: "keyword",  # import, package, use
        Token.Keyword.Pseudo: "keyword",  # self in some contexts
        Token.Keyword.Reserved: "keyword",
        Token.Keyword.Type: "type_annotation",  # class in type context

        # ===== Names (Identifiers) =====
        Token.Name: "identifier",
        Token.Name.Attribute: "identifier",  # object.attribute
        Token.Name.Builtin: "builtin_function",  # print, len, range
        Token.Name.Builtin.Pseudo: "special_identifier",  # self, this, super
        Token.Name.Class: "class_name",
        Token.Name.Constant: "identifier",  # Constants like MAX_SIZE
        Token.Name.Decorator: "decorator",  # @decorator
        Token.Name.Entity: "identifier",
        Token.Name.Exception: "class_type",  # Exception types
        Token.Name.Function: "function_name",
        Token.Name.Function.Magic: "builtin_function",  # __init__, __str__
        Token.Name.Label: "identifier",
        Token.Name.Namespace: "identifier",  # Module names
        Token.Name.Other: "identifier",
        Token.Name.Property: "identifier",
        Token.Name.Tag: "keyword",  # HTML/XML tags
        Token.Name.Variable: "identifier",
        Token.Name.Variable.Class: "special_identifier",  # cls
        Token.Name.Variable.Global: "identifier",
        Token.Name.Variable.Instance: "special_identifier",  # self
        Token.Name.Variable.Magic: "special_identifier",  # __name__

        # ===== Literals =====
        Token.Literal: "string_literal",
        Token.Literal.Date: "string_literal",

        # Strings
        Token.Literal.String: "string_literal",
        Token.Literal.String.Affix: "string_literal",  # r, f, u prefixes
        Token.Literal.String.Backtick: "string_literal",  # `template string`
        Token.Literal.String.Char: "string_literal",  # 'c'
        Token.Literal.String.Delimiter: "string_literal",  # String delimiters
        Token.Literal.String.Doc: "doc_string",  # """Docstrings"""
        Token.Literal.String.Double: "string_literal",  # "double quoted"
        Token.Literal.String.Escape: "escape_sequence",  # \n, \t, etc.
        Token.Literal.String.Heredoc: "string_literal",
        Token.Literal.String.Interpol: "string_literal",  # ${interpolation}
        Token.Literal.String.Other: "string_literal",
        Token.Literal.String.Regex: "string_literal",  # /regex/
        Token.Literal.String.Single: "string_literal",  # 'single quoted'
        Token.Literal.String.Symbol: "string_literal",  # :symbol

        # Numbers
        Token.Literal.Number: "number_literal",
        Token.Literal.Number.Bin: "number_literal",  # 0b1010
        Token.Literal.Number.Float: "number_literal",  # 3.14
        Token.Literal.Number.Hex: "number_literal",  # 0xFF
        Token.Literal.Number.Integer: "number_literal",
        Token.Literal.Number.Integer.Long: "number_literal",
        Token.Literal.Number.Oct: "number_literal",  # 0o755

        # ===== Operators =====
        Token.Operator: "operator",
        Token.Operator.Word: "keyword_operator",  # and, or, not, in, is

        # ===== Punctuation =====
        Token.Punctuation: "punctuation",
        Token.Punctuation.Marker: "punctuation",  # @ in @decorator context

        # ===== Comments =====
        Token.Comment: "comment",
        Token.Comment.Hashbang: "comment",  # #!/usr/bin/env python
        Token.Comment.Multiline: "comment",  # /* ... */
        Token.Comment.Preproc: "keyword",  # #include, #define
        Token.Comment.PreprocFile: "string_literal",  # #include "file.h"
        Token.Comment.Single: "comment",  # // comment
        Token.Comment.Special: "comment",  # TODO, FIXME

        # ===== Generic (diffs, errors, etc.) =====
        Token.Generic: "identifier",
        Token.Generic.Deleted: "error",  # - deleted line
        Token.Generic.Emph: "identifier",  # *emphasis*
        Token.Generic.Error: "error",
        Token.Generic.Heading: "keyword",  # # Heading
        Token.Generic.Inserted: "success",  # + inserted line
        Token.Generic.Output: "identifier",
        Token.Generic.Prompt: "keyword",  # >>> prompt
        Token.Generic.Strong: "identifier",  # **strong**
        Token.Generic.Subheading: "keyword",
        Token.Generic.Traceback: "error",

        # ===== Other =====
        Token.Error: "error",
        Token.Other: "identifier",
        Token.Whitespace: "whitespace",  # Usually not styled
    }

    def map_token(self, token_type: Token) -> str:
        """Map Pygments token type to semantic category.

        Uses exact match first, then walks up token hierarchy to find
        the most specific semantic category.

        Args:
            token_type: Pygments token type (e.g., Token.Keyword.Type)

        Returns:
            Semantic category name (e.g., "keyword", "string_literal")

        Example:
            >>> mapper = TokenMapper()
            >>> mapper.map_token(Token.Keyword.Type)
            'type_annotation'
            >>> mapper.map_token(Token.Name.Function)
            'function_name'
            >>> mapper.map_token(Token.Name.Function.Magic)
            'builtin_function'
        """
        # Try exact match first
        if token_type in self.TOKEN_TO_SEMANTIC:
            return self.TOKEN_TO_SEMANTIC[token_type]

        # Walk up token hierarchy
        current = token_type
        while current.parent is not None:
            if current.parent in self.TOKEN_TO_SEMANTIC:
                return self.TOKEN_TO_SEMANTIC[current.parent]
            current = current.parent

        # Default fallback
        return "default"
```

---

### Module 3: Semantic Mapping

**File**: `src/claude_agent_sdk/rendering/syntax/semantic_mapping.py`

```python
"""Semantic category to theme color mapping.

This module provides the customization layer between semantic categories
(from TokenMapper) and theme colors. Users can create custom mappings
to achieve different syntax coloring schemes.

Usage:
    >>> # Use default Claude CLI mapping
    >>> mapping = SemanticMapping.claude_default()
    >>> mapping.get_theme_category("keyword")
    'tool_use'  # Maps to blue
    >>>
    >>> # Customize for specific language
    >>> custom = mapping.customize({
    ...     "comment": "metadata",  # Dim instead of green
    ...     "string_literal": "success"  # Green instead of red
    ... })
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class SemanticMapping:
    """Maps semantic categories to theme category names.

    This is the customization layer where users can override how
    syntax elements map to theme colors. For example, you could
    make all comments dim instead of green, or make strings cyan
    instead of red.

    The mapping is extensible - new semantic categories can be added
    without breaking existing themes (they'll use the default fallback).

    Attributes:
        mappings: Dict mapping semantic category name to theme category name

    Example:
        >>> mapping = SemanticMapping()
        >>> mapping.get_theme_category("keyword")
        'tool_use'  # Keywords map to blue (tool_use style)
    """

    mappings: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize with Claude CLI default mappings if empty."""
        if not self.mappings:
            self.mappings = self._get_claude_defaults()

    @staticmethod
    def _get_claude_defaults() -> Dict[str, str]:
        """Get default mappings matching Claude CLI (from Story 1).

        Returns:
            Dict mapping semantic categories to theme categories
        """
        return {
            # Keywords & Control Flow
            "keyword": "tool_use",              # blue
            "keyword_operator": "tool_use",     # blue (and, or, not)

            # Literals
            "string_literal": "error",          # red
            "escape_sequence": "error",         # red
            "number_literal": "success",        # green
            "boolean_literal": "info",          # cyan

            # Comments & Documentation
            "comment": "success",               # green
            "doc_string": "success",            # green

            # Types & Classes
            "type_annotation": "info",          # cyan
            "class_type": "info",               # cyan (in type hints)
            "class_name": "assistant_message",  # white (in definition)

            # Functions & Identifiers
            "builtin_function": "tool_use",     # blue
            "function_name": "assistant_message",  # white
            "decorator": "assistant_message",      # white
            "identifier": "assistant_message",     # white

            # Special Identifiers
            "special_identifier": "info",       # cyan (self, this, cls)

            # Operators & Punctuation
            "operator": "assistant_message",    # white
            "punctuation": "assistant_message", # white

            # Whitespace
            "whitespace": "assistant_message",  # no styling

            # Fallbacks
            "default": "assistant_message",     # white
            "error": "error",                   # red (for syntax errors)
            "success": "success",               # green (for diffs)
        }

    @classmethod
    def claude_default(cls) -> 'SemanticMapping':
        """Create mapping with Claude CLI defaults.

        Returns:
            SemanticMapping configured to match Claude CLI rendering
        """
        return cls(mappings=cls._get_claude_defaults())

    def get_theme_category(self, semantic_category: str) -> str:
        """Get theme category name for a semantic category.

        Args:
            semantic_category: Semantic category from TokenMapper
                             (e.g., "keyword", "string_literal")

        Returns:
            Theme category name (e.g., "tool_use", "error")

        Example:
            >>> mapping = SemanticMapping()
            >>> mapping.get_theme_category("keyword")
            'tool_use'
            >>> mapping.get_theme_category("string_literal")
            'error'
        """
        return self.mappings.get(semantic_category, self.mappings.get("default", "assistant_message"))

    def customize(self, overrides: Dict[str, str]) -> 'SemanticMapping':
        """Create customized mapping with overrides.

        Args:
            overrides: Dict mapping semantic categories to new theme categories

        Returns:
            New SemanticMapping with overrides applied

        Example:
            >>> base = SemanticMapping.claude_default()
            >>> custom = base.customize({
            ...     "comment": "metadata",     # Dim comments
            ...     "string_literal": "success"  # Green strings
            ... })
        """
        new_mappings = self.mappings.copy()
        new_mappings.update(overrides)
        return SemanticMapping(mappings=new_mappings)

    def validate(self, theme: 'Theme') -> list[str]:
        """Validate that all theme categories exist in theme.

        Args:
            theme: Theme to validate against

        Returns:
            List of invalid theme category names (empty if all valid)

        Example:
            >>> mapping = SemanticMapping()
            >>> theme = Theme.claude_code_default()
            >>> errors = mapping.validate(theme)
            >>> if errors:
            ...     print(f"Invalid categories: {errors}")
        """
        invalid = []
        for semantic_cat, theme_cat in self.mappings.items():
            if not hasattr(theme, theme_cat):
                invalid.append(f"{semantic_cat} -> {theme_cat}")
        return invalid
```

---

### Module 4: Structured Data Formatter

**File**: `src/claude_agent_sdk/rendering/syntax/structured_formatter.py`

```python
"""Semantic formatter for structured data (JSON/YAML).

This module provides type-aware formatting for data formats where
coloring is based on value types rather than syntax tokens.

JSON Example:
    {
        "name": "value",     # key (dim), string value (green)
        "count": 42,         # key (dim), number value (green)
        "active": true       # key (dim), boolean (cyan)
    }

YAML Example:
    name: value              # key (blue), string value (red)
    count: 42                # key (blue), number value (green)
    active: true             # key (blue), boolean (cyan)

Usage:
    >>> formatter = StructuredDataFormatter(theme, semantic_mapping)
    >>> json_str = '{"status": "ok", "count": 42}'
    >>> formatted = formatter.format_json(json_str)
"""

import json
import re
from typing import Any, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class StructuredDataFormatter:
    """Formats structured data with type-aware semantic coloring.

    Unlike syntax highlighting which colors based on syntax elements,
    this formatter colors based on data types (string, number, boolean, null).
    This matches Claude CLI's rendering of JSON/YAML in tool results.

    Supported Formats:
        - JSON: Semantic coloring for keys, values, and structure
        - YAML: Semantic coloring for keys, values, and comments

    Attributes:
        theme: Theme instance for styling
        semantic_mapping: Mapping from semantic categories to theme colors
    """

    def __init__(self, theme: 'Theme', semantic_mapping: 'SemanticMapping'):
        """Initialize formatter.

        Args:
            theme: Theme instance
            semantic_mapping: Semantic to theme category mapping
        """
        self.theme = theme
        self.semantic_mapping = semantic_mapping

    def format_json(self, data: str) -> str:
        """Format JSON with semantic type-based coloring.

        Color Mapping (from Story 1):
            - Keys: dim (metadata)
            - String values: green (success)
            - Number values: green (success)
            - Boolean values: cyan (info)
            - Null values: cyan (info)
            - Structure ({}, [], :, ,): white (assistant_message)

        Args:
            data: JSON string

        Returns:
            ANSI-styled JSON string

        Example:
            >>> formatter = StructuredDataFormatter(theme, mapping)
            >>> json_str = '{"name": "test", "count": 42, "active": true}'
            >>> print(formatter.format_json(json_str))
            # Output with colored: keys dim, "test" green, 42 green, true cyan
        """
        try:
            parsed = json.loads(data)
            return self._format_json_value(parsed, indent=0)
        except json.JSONDecodeError:
            # Not valid JSON - return as-is
            return data

    def _format_json_value(self, value: Any, indent: int) -> str:
        """Recursively format JSON value with type-aware coloring.

        Args:
            value: Python value (dict, list, str, int, float, bool, None)
            indent: Current indentation level

        Returns:
            Formatted string with ANSI color codes
        """
        indent_str = "  " * indent

        if isinstance(value, dict):
            if not value:
                return self._style("{}", "assistant_message")

            lines = [self._style("{", "assistant_message")]
            items = list(value.items())

            for i, (key, val) in enumerate(items):
                # Key (dim)
                key_styled = self._style(f'"{key}"', "metadata")
                # Colon (white)
                colon = self._style(": ", "assistant_message")
                # Value (recursive)
                val_formatted = self._format_json_value(val, indent + 1)
                # Comma (white)
                comma = self._style(",", "assistant_message") if i < len(items) - 1 else ""

                lines.append(f"{indent_str}  {key_styled}{colon}{val_formatted}{comma}")

            lines.append(indent_str + self._style("}", "assistant_message"))
            return "\n".join(lines)

        elif isinstance(value, list):
            if not value:
                return self._style("[]", "assistant_message")

            lines = [self._style("[", "assistant_message")]

            for i, item in enumerate(value):
                item_formatted = self._format_json_value(item, indent + 1)
                comma = self._style(",", "assistant_message") if i < len(value) - 1 else ""
                lines.append(f"{indent_str}  {item_formatted}{comma}")

            lines.append(indent_str + self._style("]", "assistant_message"))
            return "\n".join(lines)

        elif isinstance(value, str):
            # String values (green)
            return self._style(f'"{value}"', "success")

        elif isinstance(value, bool):
            # Boolean (cyan) - check bool before int!
            return self._style(str(value).lower(), "info")

        elif value is None:
            # Null (cyan)
            return self._style("null", "info")

        elif isinstance(value, (int, float)):
            # Numbers (green)
            return self._style(str(value), "success")

        else:
            # Unknown type - no styling
            return str(value)

    def format_yaml(self, data: str) -> str:
        """Format YAML with semantic coloring.

        Color Mapping (from Story 1):
            - Keys: blue (tool_use)
            - String values: red (error)
            - Number values: green (success)
            - Boolean/null values: cyan (info)
            - Comments: green (success)

        Args:
            data: YAML string

        Returns:
            ANSI-styled YAML string

        Note:
            Requires PyYAML. If not installed, returns original data.
        """
        if not YAML_AVAILABLE:
            return data

        try:
            # YAML formatting is line-based (simpler than JSON)
            lines = data.split('\n')
            formatted_lines = []

            for line in lines:
                formatted_lines.append(self._format_yaml_line(line))

            return '\n'.join(formatted_lines)

        except yaml.YAMLError:
            # Not valid YAML - return as-is
            return data

    def _format_yaml_line(self, line: str) -> str:
        """Format a single YAML line with semantic coloring.

        Args:
            line: YAML line

        Returns:
            Formatted line with ANSI codes
        """
        # Comment (green)
        if '#' in line:
            code_part, comment_part = line.split('#', 1)
            comment_styled = self._style(f"#{comment_part}", "success")
            if code_part.strip():
                code_styled = self._format_yaml_line(code_part.rstrip())
                return f"{code_styled}{comment_styled}"
            else:
                return f"{code_part}{comment_styled}"

        # Key-value pair
        if ':' in line and not line.strip().startswith('-'):
            key_part, value_part = line.split(':', 1)

            # Key (blue)
            key_styled = self._style(key_part, "tool_use")
            colon = self._style(":", "assistant_message")

            # Value (type-based)
            value = value_part.strip()
            if not value:
                return f"{key_styled}{colon}"
            elif value in ('true', 'false', 'True', 'False'):
                value_styled = self._style(value, "info")  # cyan
            elif value in ('null', 'None', '~'):
                value_styled = self._style(value, "info")  # cyan
            elif value.replace('.', '').replace('-', '').isdigit():
                value_styled = self._style(value, "success")  # green (number)
            else:
                # String (red)
                value_styled = self._style(value, "error")

            # Preserve leading whitespace
            leading_space = value_part[:len(value_part) - len(value_part.lstrip())]
            return f"{key_styled}{colon}{leading_space}{value_styled}"

        # No formatting needed
        return line

    def _style(self, text: str, semantic_category: str) -> str:
        """Apply ANSI styling based on semantic category.

        Args:
            text: Text to style
            semantic_category: Semantic category (e.g., "success", "info")

        Returns:
            ANSI-styled text
        """
        from claude_agent_sdk.rendering.ansi import ANSIEncoder

        # Get theme category from semantic mapping
        theme_category = self.semantic_mapping.get_theme_category(semantic_category)

        # Get style rule from theme
        if hasattr(self.theme, theme_category):
            style_rule = getattr(self.theme, theme_category)
            encoder = ANSIEncoder()
            return encoder.encode(text, style_rule)

        # No styling
        return text

    def detect_format(self, text: str) -> Optional[str]:
        """Detect if text is JSON or YAML.

        Args:
            text: Text to analyze

        Returns:
            "json", "yaml", or None

        Example:
            >>> formatter.detect_format('{"key": "value"}')
            'json'
            >>> formatter.detect_format('key: value')
            'yaml'
        """
        text = text.strip()

        # Try JSON first (most specific)
        if text.startswith(('{', '[')):
            try:
                json.loads(text)
                return "json"
            except json.JSONDecodeError:
                pass

        # Try YAML (more permissive)
        if YAML_AVAILABLE and (':' in text or text.startswith('-')):
            try:
                yaml.safe_load(text)
                return "yaml"
            except yaml.YAMLError:
                pass

        return None
```

---

### Module 5: Syntax Highlighter (Orchestrator)

**File**: `src/claude_agent_sdk/rendering/syntax/highlighter.py`

```python
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
from typing import Optional

from .language_registry import LanguageRegistry, LanguageSpec
from .token_mapper import TokenMapper
from .semantic_mapping import SemanticMapping
from .structured_formatter import StructuredDataFormatter


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
        semantic_mapping: Optional[SemanticMapping] = None,
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
        language_hint: Optional[str] = None,
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
        from claude_agent_sdk.rendering.ansi import ANSIEncoder

        if hasattr(self.theme, theme_category):
            style_rule = getattr(self.theme, theme_category)
            encoder = ANSIEncoder()
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
```

---

### Module 6: __init__.py

**File**: `src/claude_agent_sdk/rendering/syntax/__init__.py`

```python
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

from .language_registry import LanguageRegistry, LanguageSpec
from .token_mapper import TokenMapper
from .semantic_mapping import SemanticMapping
from .structured_formatter import StructuredDataFormatter
from .highlighter import SyntaxHighlighter

__all__ = [
    "LanguageRegistry",
    "LanguageSpec",
    "TokenMapper",
    "SemanticMapping",
    "StructuredDataFormatter",
    "SyntaxHighlighter",
]
```

---

## Integration Changes

### theme.py

Add `semantic_mapping` field to `Theme` class:

```python
@dataclass
class Theme:
    """Theme with semantic mapping support."""

    # ... existing fields ...

    # Syntax highlighting mapping (optional)
    semantic_mapping: Optional['SemanticMapping'] = None

    @classmethod
    def claude_code_default(cls) -> 'Theme':
        """Create Claude Code default theme."""
        from claude_agent_sdk.rendering.syntax import SemanticMapping

        theme = cls(
            # ... existing theme config ...
        )

        # Add default semantic mapping
        theme.semantic_mapping = SemanticMapping.claude_default()

        return theme
```

### config.py

Add syntax highlighting configuration:

```python
@dataclass
class RendererConfig:
    """Renderer configuration."""

    # ... existing fields ...

    # Enable syntax highlighting (requires pygments)
    enable_syntax_highlighting: bool = True
```

### formatters.py

Integrate syntax highlighter:

```python
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

class MessageFormatter:
    def __init__(self, config: RendererConfig):
        self.config = config
        self.theme = config.theme

        # Initialize syntax highlighter
        if config.enable_syntax_highlighting and self.theme.semantic_mapping:
            self.syntax_highlighter = SyntaxHighlighter(
                theme=self.theme,
                semantic_mapping=self.theme.semantic_mapping,
                enabled=True
            )
        else:
            self.syntax_highlighter = None

    def _format_code_block(self, code: str, language: Optional[str] = None) -> str:
        """Format code block with optional syntax highlighting."""
        if self.syntax_highlighter:
            return self.syntax_highlighter.highlight(code, language_hint=language)
        else:
            # Fallback to plain code_block style
            return self._style(code, "code_block")

    def _format_tool_result_content(self, content: str) -> str:
        """Format tool result content with auto-detection."""
        # Try to detect structured data
        if self.syntax_highlighter:
            detected_format = self.syntax_highlighter.structured_formatter.detect_format(content)
            if detected_format:
                return self.syntax_highlighter.highlight(content, language_hint=detected_format)

        # Fallback to plain formatting
        return content
```

### pyproject.toml

Add Pygments as optional dependency:

```toml
[project.optional-dependencies]
syntax = [
    "pygments>=2.17.0",
]
full = [
    "pygments>=2.17.0",
]
```

---

## Testing Strategy

### Unit Tests

**Test TokenMapper**:
```python
def test_token_mapper_keywords():
    from pygments.token import Token
    mapper = TokenMapper()

    assert mapper.map_token(Token.Keyword) == "keyword"
    assert mapper.map_token(Token.Keyword.Type) == "type_annotation"
    assert mapper.map_token(Token.Keyword.Constant) == "boolean_literal"

def test_token_mapper_hierarchy():
    """Test parent token fallback."""
    from pygments.token import Token
    mapper = TokenMapper()

    # Token.Name.Function.Magic should fall back to builtin_function
    assert mapper.map_token(Token.Name.Function.Magic) == "builtin_function"
```

**Test LanguageRegistry**:
```python
def test_language_detection():
    lang = LanguageRegistry.detect(hint="py")
    assert lang.name == "Python"
    assert lang.pygments_lexer == "python"

    lang = LanguageRegistry.detect(hint="typescript")
    assert lang.pygments_lexer == "typescript"

def test_json_uses_semantic_formatter():
    lang = LanguageRegistry.detect(hint="json")
    assert lang.semantic_formatter == "json"
```

**Test SemanticMapping**:
```python
def test_semantic_mapping_defaults():
    mapping = SemanticMapping.claude_default()

    assert mapping.get_theme_category("keyword") == "tool_use"
    assert mapping.get_theme_category("string_literal") == "error"
    assert mapping.get_theme_category("comment") == "success"

def test_semantic_mapping_customization():
    base = SemanticMapping.claude_default()
    custom = base.customize({"comment": "metadata"})

    assert custom.get_theme_category("comment") == "metadata"
    assert base.get_theme_category("comment") == "success"  # Original unchanged
```

**Test StructuredDataFormatter**:
```python
def test_json_formatting():
    theme = Theme.claude_code_default()
    mapping = SemanticMapping.claude_default()
    formatter = StructuredDataFormatter(theme, mapping)

    json_str = '{"status": "ok", "count": 42, "active": true, "error": null}'
    result = formatter.format_json(json_str)

    # Verify contains ANSI codes for different types
    assert "status" in result  # Key
    assert "ok" in result      # String
    assert "42" in result      # Number
    assert "true" in result    # Boolean
    assert "null" in result    # Null

def test_yaml_formatting():
    theme = Theme.claude_code_default()
    mapping = SemanticMapping.claude_default()
    formatter = StructuredDataFormatter(theme, mapping)

    yaml_str = "name: test\ncount: 42\nactive: true"
    result = formatter.format_yaml(yaml_str)

    assert "name" in result
    assert "test" in result
    assert "42" in result
```

**Test SyntaxHighlighter**:
```python
def test_python_highlighting():
    theme = Theme.claude_code_default()
    highlighter = SyntaxHighlighter(theme)

    code = 'def hello(name: str) -> None:\n    print(f"Hello, {name}!")'
    result = highlighter.highlight(code, language_hint="python")

    # Verify ANSI codes present
    assert '\x1b[' in result  # Has ANSI codes
    assert 'def' in result
    assert 'hello' in result

def test_json_routing_to_semantic():
    """Test that JSON uses semantic formatter, not Pygments."""
    theme = Theme.claude_code_default()
    highlighter = SyntaxHighlighter(theme)

    json_str = '{"key": "value"}'
    result = highlighter.highlight(json_str, language_hint="json")

    # Should use StructuredDataFormatter
    assert "key" in result
    assert "value" in result

def test_graceful_degradation_no_pygments():
    """Test fallback when Pygments not installed."""
    theme = Theme.claude_code_default()
    highlighter = SyntaxHighlighter(theme)
    highlighter._pygments_available = False

    code = "def hello(): pass"
    result = highlighter.highlight(code, language_hint="python")

    # Should fallback to plain code_block style
    assert code in result
```

### Integration Tests

```python
def test_full_code_block_rendering():
    """Test complete pipeline from code fence to styled output."""
    config = RendererConfig(
        theme=Theme.claude_code_default(),
        enable_syntax_highlighting=True
    )
    formatter = MessageFormatter(config)

    message = AssistantMessage(content=[
        TextBlock(text="Example:\n\n```python\ndef add(a: int, b: int) -> int:\n    return a + b\n```")
    ])

    rendered = formatter.format_message(message)

    # Verify syntax highlighting applied
    assert 'def' in rendered
    assert 'int' in rendered
    assert 'return' in rendered

def test_tool_result_json_formatting():
    """Test tool result with JSON auto-detection."""
    config = RendererConfig(
        theme=Theme.claude_code_default(),
        enable_syntax_highlighting=True
    )
    formatter = MessageFormatter(config)

    result = ToolResultBlock(
        tool_use_id="test",
        content='{"status": "success", "count": 42}'
    )

    rendered = formatter.format_tool_result(result)

    # Verify JSON formatted semantically
    assert "status" in rendered
    assert "success" in rendered
    assert "42" in rendered
```

---

## Documentation Requirements (Story 12)

As you implement this story, document:

1. **Module docstrings**: Each .py file needs comprehensive module-level docs
2. **Class docstrings**: All classes need purpose, attributes, usage examples
3. **Method docstrings**: All public methods need Args, Returns, Examples
4. **Inline comments**: Complex token mapping logic needs explanatory comments
5. **Architecture docs**: See Story 12 for full architecture documentation requirements

---

## Implementation Guidance

### Phased Approach

**Phase 1**: Core modules (2h)
1. Create `syntax/` directory
2. Implement `language_registry.py` with 20+ languages
3. Implement `token_mapper.py` with complete token mapping
4. Implement `semantic_mapping.py` with Claude defaults

**Phase 2**: Formatters (1h)
5. Implement `structured_formatter.py` for JSON/YAML
6. Implement `highlighter.py` orchestrator

**Phase 3**: Integration (1h)
7. Modify `theme.py`, `config.py`, `formatters.py`
8. Add Pygments to `pyproject.toml`
9. Write tests
10. Validate against Claude CLI

### Adding New Languages

To add support for a new language:

```python
# In language_registry.py, add to LANGUAGES dict:
"scala": LanguageSpec(
    name="Scala",
    aliases=["scala"],
    pygments_lexer="scala",
    category="general_purpose"
),
```

That's it! No code changes needed.

### Custom Theme Example

```python
# Create theme with custom syntax coloring
theme = Theme.claude_code_default()

# Make comments dim instead of green
custom_mapping = theme.semantic_mapping.customize({
    "comment": "metadata"  # Use dim style
})

theme.semantic_mapping = custom_mapping

# Use with highlighter
highlighter = SyntaxHighlighter(theme)
```

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Pygments not installed | High | Medium | Graceful fallback to plain code_block style |
| Performance overhead | Medium | Low | Only highlight code blocks, cache lexers |
| Token mapping gaps | Low | Medium | Comprehensive fallback chain in TokenMapper |
| YAML not installed | Low | Low | Check YAML_AVAILABLE, fallback gracefully |

---

## Out of Scope

**Not included in this story**:
- ❌ Pattern detection (issue #s, hex codes) → Story 9
- ❌ Custom Pygments styles → Future enhancement
- ❌ Language auto-detection from content → Use fence hints
- ❌ Syntax error highlighting → Future enhancement

---

## Completion Checklist

- [ ] Module 1: `language_registry.py` implemented with 20+ languages
- [ ] Module 2: `token_mapper.py` implemented with 100+ token mappings
- [ ] Module 3: `semantic_mapping.py` implemented with Claude defaults
- [ ] Module 4: `structured_formatter.py` implemented for JSON/YAML
- [ ] Module 5: `highlighter.py` orchestrator implemented
- [ ] Module 6: `__init__.py` with exports
- [ ] Integration: `theme.py` updated with `semantic_mapping` field
- [ ] Integration: `config.py` updated with `enable_syntax_highlighting`
- [ ] Integration: `formatters.py` integrated with `SyntaxHighlighter`
- [ ] Dependencies: `pygments>=2.17` added to `pyproject.toml`
- [ ] Tests: All unit tests passing (token mapper, registry, formatters)
- [ ] Tests: Integration tests passing (full pipeline)
- [ ] Validation: Manual testing against Claude CLI outputs
- [ ] Documentation: All modules, classes, methods documented (Story 12)
- [ ] Code review: Architecture reviewed
- [ ] Story marked complete in index.md

---

**Document Version**: 2.0
**Created**: 2025-11-08 23:45
**Author**: Claude Agent SDK Team
**Replaces**: Stories 4 & 10 (archived)
