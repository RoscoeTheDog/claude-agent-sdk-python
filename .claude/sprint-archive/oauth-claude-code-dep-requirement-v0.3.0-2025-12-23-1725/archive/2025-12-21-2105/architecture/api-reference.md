# API Reference - Syntax Highlighting

**Version**: 1.0
**Created**: 2025-11-09
**Sprint**: 1.5 - Color Theme Accuracy & Tool Formatting

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Public Classes](#public-classes)
3. [Configuration](#configuration)
4. [Code Examples](#code-examples)

---

## Quick Start

```python
from claude_agent_sdk.rendering import RendererConfig, Theme
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

# Create theme and highlighter
theme = Theme.claude_code_default()
highlighter = SyntaxHighlighter(theme)

# Highlight code
code = 'def hello(): print("world")'
highlighted = highlighter.highlight(code, language_hint="python")
print(highlighted)
```

---

## Public Classes

### `SyntaxHighlighter`

Main entry point for syntax highlighting. Orchestrates language detection, token mapping, and styling.

**Module**: `claude_agent_sdk.rendering.syntax.highlighter`

#### Constructor

```python
def __init__(
    self,
    theme: Theme,
    semantic_mapping: SemanticMapping | None = None,
    enabled: bool = True
)
```

**Parameters**:
- `theme` (Theme): Theme instance containing color styles
- `semantic_mapping` (SemanticMapping | None): Custom semantic mapping (uses Claude default if None)
- `enabled` (bool): Whether highlighting is enabled (default: True)

**Example**:

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter, SemanticMapping

# Basic usage (Claude defaults)
highlighter = SyntaxHighlighter(Theme.claude_code_default())

# Custom semantic mapping
custom_mapping = SemanticMapping.claude_default().customize({
    "comment": "metadata"  # Make comments gray instead of green
})
highlighter = SyntaxHighlighter(
    Theme.claude_code_default(),
    semantic_mapping=custom_mapping
)

# Disabled highlighting
highlighter = SyntaxHighlighter(Theme.claude_code_default(), enabled=False)
```

#### Methods

##### `highlight()`

```python
def highlight(
    self,
    code: str,
    language_hint: str | None = None,
    context: str = "code_block"
) -> str
```

Highlight code using appropriate strategy (Pygments or semantic formatter).

**Parameters**:
- `code` (str): Source code to highlight
- `language_hint` (str | None): Language fence hint (e.g., "python", "js", "json")
- `context` (str): Usage context, either "code_block" or "tool_result" (default: "code_block")

**Returns**:
- `str`: ANSI-styled code with color codes, or plain text if highlighting disabled/unavailable

**Behavior**:
1. Detect language from hint using `LanguageRegistry`
2. Route to semantic formatter (JSON/YAML) or Pygments (general languages)
3. Apply token/type-based coloring via theme
4. Return styled output with ANSI codes

**Graceful Degradation**:
- Unknown language → plain text
- Pygments not installed → plain text
- Highlighting disabled → plain text

**Example**:

```python
# Python code
python_code = '''
def factorial(n):
    """Calculate factorial recursively."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''
highlighted = highlighter.highlight(python_code, language_hint="python")

# JSON data
json_data = '{"name": "Alice", "age": 30, "active": true}'
highlighted = highlighter.highlight(json_data, language_hint="json")

# Unknown language (falls back to plain)
unknown = "code in unknown language"
highlighted = highlighter.highlight(unknown, language_hint="foobar")
# Returns: "code in unknown language" (unmodified)
```

---

### `LanguageRegistry`

Central registry of supported programming languages. Provides language detection and metadata lookup.

**Module**: `claude_agent_sdk.rendering.syntax.language_registry`

#### Class Methods

##### `detect()`

```python
@classmethod
def detect(
    cls,
    hint: str | None = None,
    code: str | None = None
) -> LanguageSpec | None
```

Detect language from fence hint or code content.

**Parameters**:
- `hint` (str | None): Language fence hint (e.g., "python", "py", "json")
- `code` (str | None): Source code for content-based detection (not implemented)

**Returns**:
- `LanguageSpec | None`: Language specification if detected, None otherwise

**Example**:

```python
from claude_agent_sdk.rendering.syntax import LanguageRegistry

# Detect from fence hint
lang = LanguageRegistry.detect(hint="python")
print(lang.name)            # "Python"
print(lang.pygments_lexer)  # "python"

# Check if uses semantic formatter
lang = LanguageRegistry.detect(hint="json")
print(lang.semantic_formatter)  # "json"

# Unknown language
lang = LanguageRegistry.detect(hint="foobar")
print(lang)  # None
```

##### `get_by_id()`

```python
@classmethod
def get_by_id(cls, language_id: str) -> LanguageSpec | None
```

Get language by canonical ID (dictionary key).

**Parameters**:
- `language_id` (str): Canonical language ID (e.g., "python", "javascript")

**Returns**:
- `LanguageSpec | None`: Language specification if found, None otherwise

**Example**:

```python
lang = LanguageRegistry.get_by_id("python")
print(lang.name)  # "Python"

lang = LanguageRegistry.get_by_id("unknown")
print(lang)  # None
```

#### Attributes

##### `LANGUAGES`

```python
LANGUAGES: dict[str, LanguageSpec]
```

Dictionary of all registered languages (class attribute).

**Example**:

```python
all_langs = LanguageRegistry.LANGUAGES
print(len(all_langs))  # ~20 predefined languages

for lang_id, spec in all_langs.items():
    print(f"{lang_id}: {spec.name}")
```

---

### `LanguageSpec`

Specification for a programming language.

**Module**: `claude_agent_sdk.rendering.syntax.language_registry`

#### Attributes

```python
@dataclass
class LanguageSpec:
    name: str                        # Human-readable name
    aliases: list[str]               # Fence hint aliases
    pygments_lexer: str              # Pygments lexer name
    category: str                    # Language category
    semantic_formatter: str | None   # Optional semantic formatter
```

**Categories**:
- `"general_purpose"`: Python, JavaScript, Java, etc.
- `"data_format"`: JSON, YAML, XML
- `"markup"`: HTML, Markdown
- `"shell"`: Bash, PowerShell
- `"database"`: SQL

**Example**:

```python
from claude_agent_sdk.rendering.syntax import LanguageSpec

python_spec = LanguageSpec(
    name="Python",
    aliases=["py", "python", "python3"],
    pygments_lexer="python",
    category="general_purpose",
    semantic_formatter=None
)

json_spec = LanguageSpec(
    name="JSON",
    aliases=["json"],
    pygments_lexer="json",
    category="data_format",
    semantic_formatter="json"  # Use semantic formatter instead of Pygments
)
```

---

### `SemanticMapping`

Maps semantic categories (e.g., "keyword", "string") to theme categories (e.g., "primary", "error").

**Module**: `claude_agent_sdk.rendering.syntax.semantic_mapping`

#### Class Methods

##### `claude_default()`

```python
@classmethod
def claude_default(cls) -> SemanticMapping
```

Get Claude Code CLI default semantic mapping.

**Returns**:
- `SemanticMapping`: Default mapping matching Claude CLI colors

**Example**:

```python
from claude_agent_sdk.rendering.syntax import SemanticMapping

mapping = SemanticMapping.claude_default()
category = mapping.get_theme_category("keyword")
print(category)  # "primary" (blue)
```

#### Instance Methods

##### `get_theme_category()`

```python
def get_theme_category(self, semantic_category: str) -> str
```

Get theme category for a semantic category.

**Parameters**:
- `semantic_category` (str): Semantic category (e.g., "keyword", "string")

**Returns**:
- `str`: Theme category name (e.g., "primary", "error", "success")

**Example**:

```python
mapping = SemanticMapping.claude_default()

# Query semantic → theme mappings
print(mapping.get_theme_category("keyword"))   # "primary" (blue)
print(mapping.get_theme_category("string"))    # "error" (red)
print(mapping.get_theme_category("comment"))   # "success" (green)
print(mapping.get_theme_category("function"))  # "info" (cyan)
```

##### `customize()`

```python
def customize(self, overrides: dict[str, str]) -> SemanticMapping
```

Create new mapping with custom overrides.

**Parameters**:
- `overrides` (dict[str, str]): Semantic category → theme category overrides

**Returns**:
- `SemanticMapping`: New mapping with overrides applied

**Example**:

```python
# Make comments gray instead of green
custom = SemanticMapping.claude_default().customize({
    "comment": "metadata"  # Gray instead of green
})

# Make all literals cyan
custom = SemanticMapping.claude_default().customize({
    "string": "info",
    "number": "info",
    "literal": "info"
})
```

---

### `TokenMapper`

Maps Pygments tokens to semantic categories.

**Module**: `claude_agent_sdk.rendering.syntax.token_mapper`

#### Methods

##### `map_token()`

```python
def map_token(self, token) -> str
```

Map Pygments token to semantic category with hierarchical fallback.

**Parameters**:
- `token`: Pygments token (e.g., `Token.Keyword`, `Token.String.Doc`)

**Returns**:
- `str`: Semantic category name (e.g., "keyword", "string", "comment")

**Fallback Strategy**:
1. Try exact token match (e.g., `Token.String.Doc`)
2. Fall back to parent token (e.g., `Token.String`)
3. Ultimate fallback to `"text"`

**Example**:

```python
from pygments.token import Token
from claude_agent_sdk.rendering.syntax import TokenMapper

mapper = TokenMapper()

# Direct mapping
category = mapper.map_token(Token.Keyword)
print(category)  # "keyword"

# Hierarchical fallback (Token.String.Doc → Token.String → "string")
category = mapper.map_token(Token.String.Doc)
print(category)  # "string"

# Unknown token → "text"
category = mapper.map_token(Token.Generic.UnknownType)
print(category)  # "text"
```

---

### `StructuredDataFormatter`

Type-aware formatter for structured data (JSON, YAML).

**Module**: `claude_agent_sdk.rendering.syntax.structured_formatter`

#### Constructor

```python
def __init__(self, theme: Theme, semantic_mapping: SemanticMapping)
```

**Parameters**:
- `theme` (Theme): Theme instance
- `semantic_mapping` (SemanticMapping): Semantic mapping

#### Methods

##### `format_json()`

```python
def format_json(self, data: str) -> str
```

Format JSON with type-based coloring.

**Parameters**:
- `data` (str): JSON string

**Returns**:
- `str`: ANSI-styled JSON with type-based colors

**Color Mapping**:
- Keys → `metadata` (gray)
- String values → `success` (green)
- Number values → `success` (green)
- Boolean/null values → `info` (cyan)
- Structural chars (`{`, `}`, `:`, `,`) → `metadata` (gray)

**Example**:

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import (
    StructuredDataFormatter,
    SemanticMapping
)

formatter = StructuredDataFormatter(
    theme=Theme.claude_code_default(),
    semantic_mapping=SemanticMapping.claude_default()
)

json_data = '{"name": "Alice", "age": 30, "active": true}'
styled = formatter.format_json(json_data)
# Keys "name", "age", "active" → gray
# "Alice" → green (string)
# 30 → green (number)
# true → cyan (boolean)
```

##### `format_yaml()`

```python
def format_yaml(self, data: str) -> str
```

Format YAML with type-based coloring.

**Parameters**:
- `data` (str): YAML string

**Returns**:
- `str`: ANSI-styled YAML with type-based colors

**Example**:

```python
yaml_data = '''
name: Alice
age: 30
active: true
'''
styled = formatter.format_yaml(yaml_data)
```

---

## Configuration

### Renderer Config

Enable/disable syntax highlighting globally.

```python
from claude_agent_sdk.rendering import RendererConfig

# Enable syntax highlighting (default)
config = RendererConfig(enable_syntax_highlighting=True)

# Disable syntax highlighting
config = RendererConfig(enable_syntax_highlighting=False)
```

### Theme Configuration

Customize syntax highlighting colors via theme's `semantic_mapping` field.

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import SemanticMapping

# Create theme with custom semantic mapping
theme = Theme.claude_code_default()
theme.semantic_mapping = SemanticMapping.claude_default().customize({
    "comment": "metadata",  # Gray comments
    "string": "warning"     # Yellow/orange strings
})
```

---

## Code Examples

### Example 1: Basic Highlighting

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

theme = Theme.claude_code_default()
highlighter = SyntaxHighlighter(theme)

# Python code
code = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''

highlighted = highlighter.highlight(code, language_hint="python")
print(highlighted)
```

### Example 2: Custom Semantic Mapping

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter, SemanticMapping

# Make comments dim gray instead of green
custom_mapping = SemanticMapping.claude_default().customize({
    "comment": "metadata"
})

theme = Theme.claude_code_default()
highlighter = SyntaxHighlighter(theme, semantic_mapping=custom_mapping)

code = '# This comment will be gray\nprint("Hello")'
highlighted = highlighter.highlight(code, language_hint="python")
print(highlighted)
```

### Example 3: JSON Formatting

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

theme = Theme.claude_code_default()
highlighter = SyntaxHighlighter(theme)

json_data = '''
{
  "user": {
    "name": "Alice",
    "age": 30,
    "active": true,
    "balance": 1234.56
  }
}
'''

highlighted = highlighter.highlight(json_data, language_hint="json")
print(highlighted)
# Keys → gray
# "Alice" → green
# 30, 1234.56 → green
# true → cyan
```

### Example 4: Multiple Languages

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

theme = Theme.claude_code_default()
highlighter = SyntaxHighlighter(theme)

examples = {
    "python": 'def hello(): pass',
    "javascript": 'function hello() {}',
    "rust": 'fn hello() {}',
    "go": 'func hello() {}',
    "json": '{"hello": "world"}'
}

for lang, code in examples.items():
    highlighted = highlighter.highlight(code, language_hint=lang)
    print(f"{lang}:")
    print(highlighted)
    print()
```

### Example 5: Language Detection

```python
from claude_agent_sdk.rendering.syntax import LanguageRegistry

# Detect from various hints
hints = ["python", "py", "python3", "js", "javascript", "json"]

for hint in hints:
    lang = LanguageRegistry.detect(hint=hint)
    if lang:
        print(f"{hint} → {lang.name} (lexer: {lang.pygments_lexer})")
    else:
        print(f"{hint} → Not found")

# Output:
# python → Python (lexer: python)
# py → Python (lexer: python)
# python3 → Python (lexer: python)
# js → JavaScript (lexer: javascript)
# javascript → JavaScript (lexer: javascript)
# json → JSON (lexer: json)
```

### Example 6: Check Pygments Availability

```python
import importlib.util

# Check if Pygments is installed
pygments_available = importlib.util.find_spec("pygments") is not None

if pygments_available:
    from claude_agent_sdk.rendering import Theme
    from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

    highlighter = SyntaxHighlighter(Theme.claude_code_default())
    # Full syntax highlighting available
else:
    # Fallback: no syntax highlighting
    print("Install Pygments for syntax highlighting:")
    print("pip install claude-agent-sdk[syntax]")
```

### Example 7: Disable Highlighting

```python
from claude_agent_sdk.rendering import Theme
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

# Create highlighter with highlighting disabled
theme = Theme.claude_code_default()
highlighter = SyntaxHighlighter(theme, enabled=False)

code = 'def hello(): print("world")'
result = highlighter.highlight(code, language_hint="python")
# Returns plain text (no ANSI codes)
assert result == code
```

---

## Error Handling

### Graceful Degradation

The syntax highlighting system is designed to never throw exceptions:

```python
# Unknown language → returns plain text
highlighter.highlight("code", language_hint="unknown_lang")
# Returns: "code" (unmodified)

# Pygments not installed → returns plain text
# (no exception thrown)

# Invalid JSON → returns plain text
highlighter.highlight("{invalid json}", language_hint="json")
# Returns: "{invalid json}" (unmodified)

# Empty code → returns empty string
highlighter.highlight("", language_hint="python")
# Returns: ""
```

### Fallback Behavior

| Scenario | Behavior |
|----------|----------|
| Language not in registry | Return plain text |
| Pygments not installed | Return plain text |
| Pygments lexer fails | Return plain text |
| Invalid structured data | Return plain text |
| Highlighting disabled | Return plain text |

---

## Related Documentation

- [Architecture Overview](./syntax-highlighting-architecture.md) - System design and data flow
- [Extension Guide](./extension-guide.md) - How to add languages and customize mappings
- [README](../../../README.md) - User-facing documentation

---

**Document Version**: 1.0
**Last Updated**: 2025-11-09
**Author**: Claude Agent SDK Team
