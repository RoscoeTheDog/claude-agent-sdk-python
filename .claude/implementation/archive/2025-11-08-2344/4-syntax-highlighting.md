# Story 4: Code Syntax Highlighting Infrastructure

**Status**: unassigned
**Assignee**: unassigned
**Estimated Time**: 2 hours (reduced from 3h - scope clarified)
**Actual Time**: TBD

---

## Dependencies

- Story 1 (COMPLETED) - Provides complete ANSI color mappings from Claude CLI
- Story 2 (unassigned) - Provides accurate theme foundation
- Reference: `.claude/implementation/stories/1-color-analysis.md`

---

## Description

Add syntax highlighting support for code blocks using Pygments integration. Implement `SyntaxMapping` configuration to map Pygments tokens to theme categories, enabling customizable syntax coloring per theme.

**Scope Note**: This story focuses ONLY on code syntax highlighting within code blocks (triple-backtick fences). Structured data formatting (JSON/YAML in tool results) is handled by Story 10.

**Goal**: Achieve accurate syntax highlighting for code examples matching Claude CLI's rendering.

---

## Acceptance Criteria

### Core Infrastructure
- [ ] Add optional dependency: `pygments>=2.17` to `pyproject.toml`
- [ ] Create `src/claude_agent_sdk/rendering/syntax.py` module
- [ ] Implement `SyntaxHighlighter` class with language detection
- [ ] Graceful degradation if Pygments not installed (use plain `code_block` style)

### SyntaxMapping Configuration
- [ ] Create `SyntaxMapping` dataclass in `theme.py` with fields for all token categories
- [ ] Add `syntax_mapping: Optional[SyntaxMapping]` field to `Theme` class
- [ ] Default `SyntaxMapping` matches Story 1 findings
- [ ] Theme serialization includes syntax_mapping

### Pygments Integration
- [ ] Implement complete Pygments token → SyntaxMapping mapper
- [ ] Support languages: Python, JavaScript, TypeScript, SQL, Bash, JSON, YAML
- [ ] Handle unknown languages gracefully (fallback to plain text)
- [ ] Language detection from code fence info string (e.g., ` ```python `)

### Renderer Integration
- [ ] Add `enable_syntax_highlighting: bool = True` to `RendererConfig`
- [ ] Integrate in `_format_tool_result_content()` for code blocks
- [ ] Integrate in message formatting for code fence blocks
- [ ] Apply syntax highlighting before theme styling

---

## Technical Implementation

### Affected Files

**New Files**:
- `src/claude_agent_sdk/rendering/syntax.py` - Syntax highlighting module

**Modified Files**:
- `src/claude_agent_sdk/rendering/theme.py` - Add `SyntaxMapping` dataclass
- `src/claude_agent_sdk/rendering/config.py` - Add `enable_syntax_highlighting` config
- `src/claude_agent_sdk/rendering/formatters.py` - Integrate highlighter
- `pyproject.toml` - Add Pygments optional dependency

### SyntaxMapping Structure

Based on Story 1 findings:

```python
from dataclasses import dataclass

@dataclass
class SyntaxMapping:
    """Maps Pygments token types to Theme semantic categories.

    This allows themes to customize syntax highlighting colors by
    mapping syntax elements to existing theme categories.

    All fields contain theme category names (strings) that must exist
    in the Theme class. Invalid category names fall back to "assistant_message".

    Defaults match Claude CLI observed behavior (Story 1, 2025-11-08).
    """

    # Core syntax elements (map to theme category names)
    keyword: str = "tool_use"              # blue - def, class, if, async, SELECT
    string: str = "error"                  # red - "strings", 'literals', f"{}"
    comment: str = "success"               # green - # comments, // comments
    number: str = "success"                # green - 42, 3.14, 0xFF
    type_annotation: str = "info"          # cyan - str, int, List, Optional
    boolean: str = "info"                  # cyan - True, False, true, false
    builtin_function: str = "tool_use"     # blue - print(), len(), range()
    operator: str = "assistant_message"    # white - +, -, ==, and, =>
    function_name: str = "assistant_message"  # white - user-defined functions
    class_name: str = "assistant_message"     # white - in definition
    class_type: str = "info"               # cyan - in type hints (MyClass:...)
    decorator: str = "assistant_message"   # white - @dataclass, @property
    special_identifier: str = "info"       # cyan - self, this, cls
    punctuation: str = "assistant_message" # white - [], {}, (), ;, :, .

    # Default fallback for unclassified tokens
    default: str = "assistant_message"     # white - unknown tokens

    def validate(self, theme: 'Theme') -> list[str]:
        """Validate that all category references exist in theme.

        Args:
            theme: Theme to validate against

        Returns:
            List of invalid category names (empty if all valid)
        """
        invalid = []
        for field_name in self.__dataclass_fields__:
            category = getattr(self, field_name)
            if not hasattr(theme, category):
                invalid.append(f"{field_name} -> {category}")
        return invalid
```

### Pygments Token Mapping

Complete token mapping in `syntax.py`:

```python
from pygments.token import Token

# Comprehensive Pygments token → SyntaxMapping field mapping
TOKEN_TO_SYNTAX_CATEGORY = {
    # Keywords
    Token.Keyword: "keyword",
    Token.Keyword.Constant: "boolean",
    Token.Keyword.Declaration: "keyword",
    Token.Keyword.Namespace: "keyword",
    Token.Keyword.Pseudo: "keyword",
    Token.Keyword.Reserved: "keyword",
    Token.Keyword.Type: "type_annotation",

    # Names (identifiers)
    Token.Name: "function_name",
    Token.Name.Attribute: "function_name",
    Token.Name.Builtin: "builtin_function",
    Token.Name.Builtin.Pseudo: "special_identifier",  # self, this
    Token.Name.Class: "class_name",
    Token.Name.Constant: "function_name",
    Token.Name.Decorator: "decorator",
    Token.Name.Entity: "function_name",
    Token.Name.Exception: "class_type",
    Token.Name.Function: "function_name",
    Token.Name.Function.Magic: "builtin_function",  # __init__, __str__
    Token.Name.Label: "function_name",
    Token.Name.Namespace: "class_name",
    Token.Name.Other: "function_name",
    Token.Name.Property: "function_name",
    Token.Name.Tag: "keyword",
    Token.Name.Variable: "function_name",
    Token.Name.Variable.Class: "special_identifier",  # cls
    Token.Name.Variable.Global: "function_name",
    Token.Name.Variable.Instance: "special_identifier",  # self
    Token.Name.Variable.Magic: "special_identifier",  # __name__

    # Literals
    Token.Literal: "string",
    Token.Literal.Date: "string",
    Token.Literal.String: "string",
    Token.Literal.String.Affix: "string",
    Token.Literal.String.Backtick: "string",
    Token.Literal.String.Char: "string",
    Token.Literal.String.Delimiter: "string",
    Token.Literal.String.Doc: "comment",  # Docstrings
    Token.Literal.String.Double: "string",
    Token.Literal.String.Escape: "string",
    Token.Literal.String.Heredoc: "string",
    Token.Literal.String.Interpol: "string",
    Token.Literal.String.Other: "string",
    Token.Literal.String.Regex: "string",
    Token.Literal.String.Single: "string",
    Token.Literal.String.Symbol: "string",
    Token.Literal.Number: "number",
    Token.Literal.Number.Bin: "number",
    Token.Literal.Number.Float: "number",
    Token.Literal.Number.Hex: "number",
    Token.Literal.Number.Integer: "number",
    Token.Literal.Number.Integer.Long: "number",
    Token.Literal.Number.Oct: "number",

    # Operators
    Token.Operator: "operator",
    Token.Operator.Word: "keyword",  # and, or, not

    # Punctuation
    Token.Punctuation: "punctuation",
    Token.Punctuation.Marker: "punctuation",

    # Comments
    Token.Comment: "comment",
    Token.Comment.Hashbang: "comment",
    Token.Comment.Multiline: "comment",
    Token.Comment.Preproc: "keyword",
    Token.Comment.PreprocFile: "string",
    Token.Comment.Single: "comment",
    Token.Comment.Special: "comment",

    # Generic (for diffs, etc.)
    Token.Generic: "assistant_message",
    Token.Generic.Deleted: "error",
    Token.Generic.Emph: "assistant_message",
    Token.Generic.Error: "error",
    Token.Generic.Heading: "keyword",
    Token.Generic.Inserted: "success",
    Token.Generic.Output: "assistant_message",
    Token.Generic.Prompt: "keyword",
    Token.Generic.Strong: "assistant_message",
    Token.Generic.Subheading: "keyword",
    Token.Generic.Traceback: "error",

    # Other
    Token.Error: "error",
    Token.Other: "assistant_message",
    Token.Whitespace: "assistant_message",
}
```

### SyntaxHighlighter Implementation

```python
import importlib.util
from typing import Optional
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

class SyntaxHighlighter:
    """Applies syntax highlighting to code using Pygments and theme mappings."""

    def __init__(self, theme: 'Theme', enabled: bool = True):
        """Initialize highlighter.

        Args:
            theme: Theme containing syntax_mapping
            enabled: Whether highlighting is enabled
        """
        self.theme = theme
        self.enabled = enabled
        self._pygments_available = importlib.util.find_spec("pygments") is not None

    def highlight_code(self, code: str, language: Optional[str] = None) -> str:
        """Apply syntax highlighting to code block.

        Args:
            code: Source code to highlight
            language: Language identifier (e.g., "python", "javascript")
                     If None, attempts to guess language

        Returns:
            ANSI-styled code string

        Falls back to plain code_block style if:
        - Pygments not installed
        - Highlighting disabled
        - Language not recognized
        - Any error during highlighting
        """
        if not self.enabled or not self._pygments_available:
            return self._apply_plain_style(code)

        try:
            # Get lexer
            if language:
                lexer = get_lexer_by_name(language)
            else:
                lexer = guess_lexer(code)

            # Get syntax mapping
            mapping = self.theme.syntax_mapping or SyntaxMapping()

            # Tokenize and apply styles
            tokens = lexer.get_tokens(code)
            result = []

            for token_type, value in tokens:
                # Map token type to syntax category
                category_field = self._map_token_type(token_type)

                # Get theme category name from syntax mapping
                theme_category = getattr(mapping, category_field, "assistant_message")

                # Get style rule from theme
                if hasattr(self.theme, theme_category):
                    style_rule = getattr(self.theme, theme_category)
                    styled_value = self._apply_ansi_style(value, style_rule)
                else:
                    styled_value = value  # No styling

                result.append(styled_value)

            return ''.join(result)

        except (ClassNotFound, Exception):
            # Graceful fallback
            return self._apply_plain_style(code)

    def _map_token_type(self, token_type: 'Token') -> str:
        """Map Pygments token type to SyntaxMapping field name.

        Args:
            token_type: Pygments token type

        Returns:
            Field name in SyntaxMapping (e.g., "keyword", "string")
        """
        # Try exact match first
        if token_type in TOKEN_TO_SYNTAX_CATEGORY:
            return TOKEN_TO_SYNTAX_CATEGORY[token_type]

        # Try parent token types (e.g., Token.Name.Function → Token.Name)
        while token_type.parent is not None:
            if token_type.parent in TOKEN_TO_SYNTAX_CATEGORY:
                return TOKEN_TO_SYNTAX_CATEGORY[token_type.parent]
            token_type = token_type.parent

        # Default fallback
        return "default"

    def _apply_ansi_style(self, text: str, style_rule: 'StyleRule') -> str:
        """Apply ANSI styling to text.

        Args:
            text: Text to style
            style_rule: Style rule to apply

        Returns:
            ANSI-escaped text
        """
        # Use existing ANSI encoder from rendering module
        from claude_agent_sdk.rendering.ansi import ANSIEncoder
        encoder = ANSIEncoder()
        return encoder.encode(text, style_rule)

    def _apply_plain_style(self, code: str) -> str:
        """Apply plain code_block style without syntax highlighting.

        Args:
            code: Source code

        Returns:
            Code styled with theme.code_block
        """
        return self._apply_ansi_style(code, self.theme.code_block)
```

### Integration with Formatters

```python
# In formatters.py
class MessageFormatter:
    def __init__(self, config: RendererConfig):
        self.config = config
        self.theme = config.theme
        # Initialize syntax highlighter
        self.syntax_highlighter = SyntaxHighlighter(
            theme=self.theme,
            enabled=config.enable_syntax_highlighting
        )

    def _format_code_block(self, code: str, language: Optional[str] = None) -> str:
        """Format code block with optional syntax highlighting.

        Args:
            code: Source code
            language: Language identifier from fence (e.g., ```python)

        Returns:
            Formatted code block
        """
        if self.config.enable_syntax_highlighting:
            highlighted = self.syntax_highlighter.highlight_code(code, language)
        else:
            highlighted = self._style(code, "code_block")

        return highlighted
```

---

## Testing Strategy

### Unit Tests

```python
def test_syntax_mapping_defaults():
    """Test SyntaxMapping defaults match Story 1 findings."""
    mapping = SyntaxMapping()

    assert mapping.keyword == "tool_use"  # blue
    assert mapping.string == "error"      # red
    assert mapping.comment == "success"   # green
    assert mapping.number == "success"    # green
    assert mapping.type_annotation == "info"  # cyan


def test_syntax_mapping_validation():
    """Test syntax mapping validation against theme."""
    theme = Theme.claude_code_default()
    mapping = SyntaxMapping()

    invalid = mapping.validate(theme)
    assert len(invalid) == 0  # All categories valid


def test_pygments_token_mapping():
    """Test complete Pygments token mapping."""
    from pygments.token import Token

    # Keywords
    assert TOKEN_TO_SYNTAX_CATEGORY[Token.Keyword] == "keyword"
    assert TOKEN_TO_SYNTAX_CATEGORY[Token.Keyword.Type] == "type_annotation"

    # Strings
    assert TOKEN_TO_SYNTAX_CATEGORY[Token.Literal.String] == "string"
    assert TOKEN_TO_SYNTAX_CATEGORY[Token.Literal.String.Escape] == "string"

    # Numbers
    assert TOKEN_TO_SYNTAX_CATEGORY[Token.Literal.Number] == "number"


def test_syntax_highlighter_python():
    """Test Python code highlighting."""
    theme = Theme.claude_code_default()
    highlighter = SyntaxHighlighter(theme, enabled=True)

    code = '''def hello(name: str) -> None:
    """Greet someone."""
    print(f"Hello, {name}!")
'''

    result = highlighter.highlight_code(code, "python")

    # Verify keywords are blue
    assert_contains_ansi_color(result, "def", BRIGHT_BLUE)
    # Verify strings are red
    assert_contains_ansi_color(result, '"Greet someone."', BRIGHT_RED)
    # Verify comments are green (docstring)
    # Verify types are cyan
    assert_contains_ansi_color(result, "str", BRIGHT_CYAN)


def test_graceful_degradation_no_pygments():
    """Test fallback when Pygments not installed."""
    theme = Theme.claude_code_default()
    highlighter = SyntaxHighlighter(theme, enabled=True)

    # Mock Pygments unavailable
    highlighter._pygments_available = False

    code = "def hello(): pass"
    result = highlighter.highlight_code(code, "python")

    # Should use plain code_block style (cyan)
    assert_contains_ansi_color(result, code, CYAN)


def test_unknown_language_fallback():
    """Test fallback for unknown language."""
    theme = Theme.claude_code_default()
    highlighter = SyntaxHighlighter(theme, enabled=True)

    code = "some unknown syntax"
    result = highlighter.highlight_code(code, "nonexistent")

    # Should fallback to plain style
    assert code in result
```

### Integration Tests

```python
def test_full_code_block_rendering():
    """Test complete code block with syntax highlighting."""
    config = RendererConfig(
        theme=Theme.claude_code_default(),
        enable_syntax_highlighting=True
    )
    formatter = MessageFormatter(config)

    message = AssistantMessage(content=[
        TextBlock(text="Here's a Python example:\n\n```python\ndef add(a: int, b: int) -> int:\n    return a + b\n```")
    ])

    rendered = formatter.format_message(message)

    # Verify syntax highlighting applied
    assert 'def' in rendered
    assert 'int' in rendered
    assert 'return' in rendered
```

---

## Implementation Guidance

### Architecture Reference

- See: `stories/renderer-architecture.md` - Section: "Syntax Highlighter"
- Syntax highlighting occurs before theme application
- SyntaxMapping provides indirection layer for theme customization

### Language Detection

```python
# Extract language from code fence
fence_match = re.match(r'^```(\w+)', line)
if fence_match:
    language = fence_match.group(1)  # e.g., "python", "javascript"
```

### Performance Considerations

- Pygments lexing can be slow for large code blocks
- Consider caching lexers by language
- Skip highlighting for very large blocks (> 10k lines)

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Pygments not installed | High | Medium | Graceful fallback to plain style |
| Performance overhead | Medium | Low | Only highlight code blocks, not all text |
| Token mapping gaps | Low | Medium | Comprehensive fallback chain |
| Language detection errors | Low | Medium | Guess lexer as fallback |

---

## Out of Scope

**Not included in this story** (see other stories):
- ❌ JSON/YAML semantic coloring → Story 10
- ❌ Pattern detection (issue #s, hex codes) → Story 9
- ❌ Inline code highlighting → Already handled by theme
- ❌ Diff syntax highlighting → Future enhancement

---

## Completion Checklist

- [ ] Pygments optional dependency added to pyproject.toml
- [ ] SyntaxMapping dataclass created and documented
- [ ] TOKEN_TO_SYNTAX_CATEGORY mapping complete
- [ ] SyntaxHighlighter class implemented
- [ ] Integration with formatters complete
- [ ] Graceful degradation tested (no Pygments, unknown language)
- [ ] All unit tests passing
- [ ] Integration tests validating full rendering
- [ ] Manual validation against Claude CLI
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Story marked complete in index.md

---

**Document Version**: 1.0
**Created**: 2025-11-08 23:10
**Author**: Claude Agent SDK Team
