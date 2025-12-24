# Extension Guide - Syntax Highlighting

**Version**: 1.0
**Created**: 2025-11-09
**Sprint**: 1.5 - Color Theme Accuracy & Tool Formatting

---

## Table of Contents

1. [Adding a New Language](#adding-a-new-language)
2. [Customizing Syntax Colors](#customizing-syntax-colors)
3. [Adding New Semantic Categories](#adding-new-semantic-categories)
4. [Creating Custom Formatters](#creating-custom-formatters)
5. [Extending Token Mappings](#extending-token-mappings)
6. [Creating Custom Themes](#creating-custom-themes)

---

## Adding a New Language

### Quick Start

**Location**: `src/claude_agent_sdk/rendering/syntax/language_registry.py`

**Step 1**: Find the Pygments lexer name

```bash
# List all available Pygments lexers
python -c "from pygments.lexers import get_all_lexers; \
           [print(f'{name}: {aliases}') for name, aliases, _, _ in get_all_lexers()]" \
           | grep -i "kotlin"
```

Output: `Kotlin: ('kotlin', 'kt')`

**Step 2**: Add language to `LANGUAGES` dict

```python
# In language_registry.py
LANGUAGES: dict[str, LanguageSpec] = {
    # ... existing languages ...

    "kotlin": LanguageSpec(
        name="Kotlin",
        aliases=["kotlin", "kt"],
        pygments_lexer="kotlin",
        category="general_purpose"
    ),
}
```

**Step 3**: Test the new language

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

highlighter = SyntaxHighlighter(Theme.claude_code_default())

kotlin_code = '''
fun main() {
    println("Hello, World!")
}
'''

highlighted = highlighter.highlight(kotlin_code, language_hint="kotlin")
print(highlighted)
```

**Done!** No code changes required, just add the dictionary entry.

---

### Detailed Example: Adding Elixir Support

```python
# 1. Find Pygments lexer
# python -c "from pygments.lexers import get_all_lexers; \
#            [print(f'{name}: {aliases}') for name, aliases, _, _ in get_all_lexers()]" \
#            | grep -i "elixir"
# Output: Elixir: ('elixir', 'ex', 'exs')

# 2. Add to language_registry.py
"elixir": LanguageSpec(
    name="Elixir",
    aliases=["elixir", "ex", "exs"],
    pygments_lexer="elixir",
    category="general_purpose"
),

# 3. Test
from claude_agent_sdk.rendering.syntax import LanguageRegistry

lang = LanguageRegistry.detect(hint="elixir")
assert lang.name == "Elixir"
assert lang.pygments_lexer == "elixir"
assert "ex" in lang.aliases
```

---

### Adding Data Format Languages

For languages that should use semantic (type-based) formatting instead of Pygments:

```python
# Example: TOML (if you want type-aware coloring)
"toml": LanguageSpec(
    name="TOML",
    aliases=["toml"],
    pygments_lexer="toml",
    category="data_format",
    semantic_formatter="toml"  # Trigger semantic formatter
),
```

**Note**: If `semantic_formatter` is set, you must also implement the formatter (see [Creating Custom Formatters](#creating-custom-formatters)).

---

### Language Categories

Choose the appropriate category for your language:

| Category | Examples | Purpose |
|----------|----------|---------|
| `general_purpose` | Python, JavaScript, Java, Rust | General-purpose programming |
| `data_format` | JSON, YAML, XML, TOML | Structured data formats |
| `markup` | HTML, Markdown, LaTeX | Markup languages |
| `shell` | Bash, PowerShell, Zsh | Shell scripting |
| `database` | SQL, PL/SQL | Database query languages |

---

## Customizing Syntax Colors

### Per-Category Override

Change the theme category for a specific semantic category:

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter, SemanticMapping

# Make comments gray (metadata) instead of green (success)
custom_mapping = SemanticMapping.claude_default().customize({
    "comment": "metadata"
})

theme = Theme.claude_code_default()
highlighter = SyntaxHighlighter(theme, semantic_mapping=custom_mapping)
```

### Multiple Overrides

```python
# Custom color scheme
custom_mapping = SemanticMapping.claude_default().customize({
    "comment": "metadata",    # Gray comments
    "string": "warning",      # Yellow/orange strings
    "keyword": "info",        # Cyan keywords
    "function": "success"     # Green functions
})

highlighter = SyntaxHighlighter(
    Theme.claude_code_default(),
    semantic_mapping=custom_mapping
)
```

### Available Semantic Categories

| Category | Default Theme Category | Default Color | Example |
|----------|----------------------|---------------|---------|
| `keyword` | `primary` | Blue | `def`, `class`, `if` |
| `string` | `error` | Red | `"hello"` |
| `comment` | `success` | Green | `# comment` |
| `function` | `info` | Cyan | `foo()` |
| `class` | `primary` | Blue | `MyClass` |
| `number` | `success` | Green | `42`, `3.14` |
| `operator` | `metadata` | Gray | `+`, `-`, `*` |
| `builtin` | `info` | Cyan | `print`, `len` |
| `literal` | `info` | Cyan | `True`, `None` |
| `variable` | `text` | Default | `x`, `count` |
| `decorator` | `warning` | Yellow | `@property` |
| `escape` | `warning` | Yellow | `\n`, `\t` |
| `error` | `error` | Red | Syntax errors |
| `property` | `info` | Cyan | `obj.attr` |
| `punctuation` | `metadata` | Gray | `(`, `)`, `,` |

### Available Theme Categories

| Theme Category | Claude Default Color | Style |
|---------------|---------------------|-------|
| `primary` | Blue | - |
| `error` | Red | - |
| `success` | Green | - |
| `warning` | Yellow/Orange | - |
| `info` | Cyan | - |
| `metadata` | Gray | Dim |
| `text` | Default | - |

---

## Adding New Semantic Categories

Sometimes you want to introduce a new semantic category not covered by defaults.

### Step 1: Update Token Mapper

**Location**: `src/claude_agent_sdk/rendering/syntax/token_mapper.py`

```python
class TokenMapper:
    TOKEN_TO_SEMANTIC: dict[Any, str] = {
        # ... existing mappings ...

        # Add new token → semantic mapping
        Token.Name.Annotation: "annotation",  # New category
        Token.Name.Label: "label",            # New category
    }
```

### Step 2: Update Semantic Mapping

**Location**: `src/claude_agent_sdk/rendering/syntax/semantic_mapping.py`

```python
class SemanticMapping:
    @classmethod
    def claude_default(cls) -> 'SemanticMapping':
        return cls(mappings={
            # ... existing mappings ...

            # Map new categories to theme
            "annotation": "warning",  # Yellow/orange
            "label": "info",          # Cyan
        })
```

### Step 3: Test New Category

```python
from pygments.token import Token
from claude_agent_sdk.rendering.syntax import TokenMapper, SemanticMapping

# Test token mapping
mapper = TokenMapper()
category = mapper.map_token(Token.Name.Annotation)
assert category == "annotation"

# Test semantic mapping
mapping = SemanticMapping.claude_default()
theme_cat = mapping.get_theme_category("annotation")
assert theme_cat == "warning"
```

---

## Creating Custom Formatters

Custom formatters are needed for specialized data formats that require type-aware or context-aware formatting.

### Example: TOML Formatter

**Step 1**: Create formatter class

**Location**: `src/claude_agent_sdk/rendering/syntax/toml_formatter.py` (new file)

```python
"""TOML semantic formatter."""

from claude_agent_sdk.rendering.theme import Theme
from .semantic_mapping import SemanticMapping


class TOMLFormatter:
    """Type-aware formatter for TOML files."""

    def __init__(self, theme: Theme, semantic_mapping: SemanticMapping):
        """Initialize formatter.

        Args:
            theme: Theme instance
            semantic_mapping: Semantic mapping
        """
        self.theme = theme
        self.semantic_mapping = semantic_mapping

    def format_toml(self, data: str) -> str:
        """Format TOML with type-based coloring.

        Args:
            data: TOML string

        Returns:
            ANSI-styled TOML string
        """
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            try:
                import tomli as tomllib  # Fallback
            except ImportError:
                return data  # No TOML parser available

        try:
            parsed = tomllib.loads(data)
        except Exception:
            return data  # Invalid TOML

        # Implement type-based coloring logic
        # Similar to StructuredDataFormatter.format_json()
        return self._colorize_toml(parsed, data)

    def _colorize_toml(self, parsed: dict, original: str) -> str:
        """Apply type-based colors to TOML."""
        # Implementation details...
        pass
```

**Step 2**: Register in Language Registry

```python
# In language_registry.py
"toml": LanguageSpec(
    name="TOML",
    aliases=["toml"],
    pygments_lexer="toml",
    category="data_format",
    semantic_formatter="toml"  # Trigger custom formatter
),
```

**Step 3**: Integrate with Highlighter

**Location**: `src/claude_agent_sdk/rendering/syntax/highlighter.py`

```python
class SyntaxHighlighter:
    def __init__(self, ...):
        # ... existing init ...

        # Initialize TOML formatter
        from .toml_formatter import TOMLFormatter
        self.toml_formatter = TOMLFormatter(theme, semantic_mapping)

    def highlight(self, code: str, language_hint: str | None, ...):
        # ... detect language ...

        # Route to TOML formatter
        if lang_spec.semantic_formatter == "toml":
            return self.toml_formatter.format_toml(code)

        # ... rest of routing logic ...
```

**Step 4**: Test Custom Formatter

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

highlighter = SyntaxHighlighter(Theme.claude_code_default())

toml_data = '''
[package]
name = "my-app"
version = "1.0.0"

[dependencies]
requests = "2.28.0"
'''

highlighted = highlighter.highlight(toml_data, language_hint="toml")
# Should use type-based coloring
```

---

## Extending Token Mappings

### Adding Token Variants

If Pygments uses specialized token types you want to map differently:

```python
# In token_mapper.py
Token.String.Doc: "docstring",          # Docstrings separate from strings
Token.Comment.PreprocFile: "directive", # Preprocessor directives
Token.Name.Builtin.Pseudo: "pseudo",    # Pseudo-keywords (self, this)
```

Then update semantic mapping:

```python
# In semantic_mapping.py
"docstring": "success",   # Green
"directive": "warning",   # Yellow
"pseudo": "info",         # Cyan
```

### Language-Specific Token Handling

For language-specific token types:

```python
# In token_mapper.py
# Python-specific
Token.String.Affix: "string",  # f-string prefix

# JavaScript-specific
Token.Keyword.Reserved: "keyword",  # Reserved words

# Rust-specific
Token.Name.Attribute: "decorator",  # Attributes (#[derive])
```

---

## Creating Custom Themes

### Full Custom Theme

```python
from claude_agent_sdk.rendering import Theme, StyleRule
from claude_agent_sdk.rendering.syntax import SemanticMapping

# Create custom theme
custom_theme = Theme(
    # Message types
    user_message=StyleRule(fg_color="bright_cyan", bold=True),
    assistant_message=StyleRule(fg_color="white"),
    system_message=StyleRule(fg_color="yellow"),

    # Tool categories
    tool_use=StyleRule(fg_color="magenta"),
    tool_result=StyleRule(fg_color="green"),
    tool_error=StyleRule(fg_color="red", bold=True),

    # Semantic categories
    error=StyleRule(fg_color="red", bold=True),
    warning=StyleRule(fg_color="yellow"),
    success=StyleRule(fg_color="green"),
    info=StyleRule(fg_color="cyan"),

    # UI elements
    bullet=StyleRule(fg_color="bright_black"),
    metadata=StyleRule(fg_color="bright_black", dim=True),

    # Code categories
    code_block=StyleRule(fg_color="white"),
    inline_code=StyleRule(fg_color="yellow"),

    # Syntax highlighting mapping
    semantic_mapping=SemanticMapping.claude_default().customize({
        "keyword": "info",      # Cyan keywords
        "string": "success",    # Green strings
        "comment": "metadata"   # Gray comments
    })
)
```

### Monochrome Theme

```python
# Theme without colors (bold/dim/underline only)
monochrome = Theme(
    user_message=StyleRule(bold=True),
    assistant_message=StyleRule(),
    system_message=StyleRule(dim=True),
    error=StyleRule(bold=True, underline=True),
    warning=StyleRule(underline=True),
    success=StyleRule(bold=True),
    info=StyleRule(),
    metadata=StyleRule(dim=True),

    semantic_mapping=SemanticMapping({
        "keyword": "error",     # Use bold style
        "string": "success",    # Use bold style
        "comment": "metadata"   # Use dim style
    })
)
```

### High-Contrast Theme

```python
# High contrast for accessibility
high_contrast = Theme.claude_code_default()

# Boost contrast for syntax elements
high_contrast.semantic_mapping = SemanticMapping.claude_default().customize({
    "keyword": "primary",    # Bright blue
    "string": "error",       # Bright red
    "comment": "metadata",   # Dim gray (less important)
    "function": "success",   # Bright green
    "class": "warning"       # Bright yellow
})
```

---

## Advanced Customization

### Context-Aware Coloring

Different colors for code blocks vs. tool results:

```python
class ContextAwareHighlighter:
    """Highlighter with context-specific color mappings."""

    def __init__(self, theme: Theme):
        self.theme = theme

        # Code block mapping (standard)
        self.code_mapping = SemanticMapping.claude_default()

        # Tool result mapping (subdued)
        self.tool_mapping = SemanticMapping.claude_default().customize({
            "keyword": "metadata",   # Gray keywords
            "string": "metadata",    # Gray strings
            "comment": "metadata"    # Gray comments
        })

    def highlight(self, code: str, language_hint: str, context: str):
        """Highlight with context-aware mapping."""
        mapping = (
            self.tool_mapping if context == "tool_result"
            else self.code_mapping
        )

        highlighter = SyntaxHighlighter(self.theme, semantic_mapping=mapping)
        return highlighter.highlight(code, language_hint, context)
```

### Language-Specific Overrides

Different color schemes per language:

```python
class LanguageSpecificHighlighter:
    """Highlighter with per-language color customization."""

    def __init__(self, theme: Theme):
        self.theme = theme

        # Default mapping
        self.default_mapping = SemanticMapping.claude_default()

        # Python: Green docstrings
        self.python_mapping = SemanticMapping.claude_default().customize({
            "comment": "success"  # Green docstrings
        })

        # JavaScript: Yellow strings
        self.js_mapping = SemanticMapping.claude_default().customize({
            "string": "warning"  # Yellow strings
        })

    def highlight(self, code: str, language_hint: str):
        """Highlight with language-specific mapping."""
        mapping = {
            "python": self.python_mapping,
            "javascript": self.js_mapping,
        }.get(language_hint, self.default_mapping)

        highlighter = SyntaxHighlighter(self.theme, semantic_mapping=mapping)
        return highlighter.highlight(code, language_hint)
```

---

## Testing Extensions

### Unit Tests for New Languages

```python
# tests/test_language_extensions.py
def test_elixir_language():
    """Test Elixir language support."""
    from claude_agent_sdk.rendering.syntax import LanguageRegistry

    lang = LanguageRegistry.detect(hint="elixir")
    assert lang is not None
    assert lang.name == "Elixir"
    assert lang.pygments_lexer == "elixir"
    assert "ex" in lang.aliases

def test_elixir_highlighting():
    """Test Elixir syntax highlighting."""
    from claude_agent_sdk.rendering import Theme
    from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

    highlighter = SyntaxHighlighter(Theme.claude_code_default())

    code = 'defmodule Hello do\n  def world, do: "Hello"\nend'
    result = highlighter.highlight(code, language_hint="elixir")

    # Should contain ANSI codes
    assert "\033[" in result
    assert len(result) > len(code)
```

### Integration Tests for Custom Formatters

```python
# tests/test_toml_formatter.py
def test_toml_formatting():
    """Test TOML custom formatter."""
    from claude_agent_sdk.rendering import Theme
    from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

    highlighter = SyntaxHighlighter(Theme.claude_code_default())

    toml_data = '[package]\nname = "app"\nversion = "1.0.0"'
    result = highlighter.highlight(toml_data, language_hint="toml")

    # Should contain type-based colors
    assert "\033[" in result
```

---

## Best Practices

### 1. Language Registry Additions

- **DO**: Add all common aliases (e.g., "py", "python", "python3")
- **DO**: Use official Pygments lexer names
- **DO**: Choose appropriate category
- **DON'T**: Duplicate existing languages
- **DON'T**: Create aliases that conflict with existing languages

### 2. Semantic Mappings

- **DO**: Keep semantic categories language-agnostic ("keyword", not "python_keyword")
- **DO**: Use theme categories for actual colors
- **DO**: Test customizations with multiple languages
- **DON'T**: Hard-code colors in semantic mapping
- **DON'T**: Create too many semantic categories (keep it simple)

### 3. Custom Formatters

- **DO**: Handle errors gracefully (fallback to plain text)
- **DO**: Follow same pattern as `StructuredDataFormatter`
- **DO**: Support type-based coloring for data formats
- **DON'T**: Throw exceptions (always return string)
- **DON'T**: Duplicate logic from existing formatters

### 4. Theme Customization

- **DO**: Maintain contrast ratios for accessibility
- **DO**: Test themes in different terminal emulators
- **DO**: Provide fallback for monochrome terminals
- **DON'T**: Use colors that are too similar
- **DON'T**: Rely on truecolor support (not all terminals support it)

---

## Related Documentation

- [Architecture Overview](./syntax-highlighting-architecture.md) - System design
- [API Reference](./api-reference.md) - Public API documentation
- [README](../../../README.md) - User-facing documentation

---

**Document Version**: 1.0
**Last Updated**: 2025-11-09
**Author**: Claude Agent SDK Team
