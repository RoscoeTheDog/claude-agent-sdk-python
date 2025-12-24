# Syntax Highlighting Architecture

**Version**: 1.0
**Created**: 2025-11-09
**Sprint**: 1.5 - Color Theme Accuracy & Tool Formatting

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Module Responsibilities](#module-responsibilities)
4. [Data Flow](#data-flow)
5. [Design Decisions](#design-decisions)
6. [Extension Points](#extension-points)
7. [Terminal Compatibility](#terminal-compatibility)

---

## Overview

The syntax highlighting system provides consistent, theme-aware syntax highlighting for code blocks and tool results across 500+ programming languages. The architecture follows a modular, pipeline-based design with clean separation of concerns.

### Key Features

- **500+ Language Support**: Via Pygments lexer integration with extensible language registry
- **Semantic Coloring**: Token-agnostic semantic categories for consistent theming
- **Type-Aware Formatting**: Specialized formatters for structured data (JSON, YAML)
- **Theme Consistency**: Unified color palette across syntax and semantic elements
- **Graceful Degradation**: Works without Pygments, falls back to plain text
- **Zero Code Duplication**: Shared pipeline for code blocks and tool results

### Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Language Agnostic**: Token mapping layer abstracts language-specific details
3. **Customizable**: Users can override mappings at multiple levels
4. **Performance**: Efficient token processing with minimal overhead
5. **Extensible**: New languages, tokens, and formatters can be added without core changes

---

## Architecture Diagram

```
User Request: Highlight Python code
         |
         v
   ┌──────────────────────────────────────┐
   │   SyntaxHighlighter                  │  (Orchestrator)
   │   .highlight(code, language_hint)    │
   └──────────┬───────────────────────────┘
              |
              v
   ┌──────────────────────────────────────┐
   │   LanguageRegistry                   │  (Language Detection)
   │   .detect(hint="python")             │
   └──────────┬───────────────────────────┘
              |
              v
        LanguageSpec(
          name="Python"
          pygments_lexer="python"
          semantic_formatter=None
        )
              |
        ┌─────┴──────┐
        |            |
        v            v
   [Data Format]  [General Language]
        |            |
        v            v
  ┌─────────────┐  ┌────────────────────────┐
  │ Structured  │  │ Pygments Lexer         │
  │ Formatter   │  │ → Token Stream         │
  └──────┬──────┘  └─────────┬──────────────┘
         |                   |
         v                   v
  Type-based         ┌─────────────────────┐
  coloring           │ TokenMapper         │
         |           │ .map_token(token)   │
         |           └──────┬──────────────┘
         |                  |
         |                  v
         |           Semantic Category
         |           (e.g., "keyword")
         |                  |
         └──────┬───────────┘
                |
                v
     ┌────────────────────────┐
     │ SemanticMapping        │  (Semantic → Theme)
     │ .get_theme_category()  │
     └──────┬─────────────────┘
            |
            v
       Theme Category
       (e.g., "primary")
            |
            v
     ┌────────────────────┐
     │ Theme              │  (Color Lookup)
     │ .get_style(cat)    │
     └──────┬─────────────┘
            |
            v
        StyleRule
        (fg_color, bold, etc.)
            |
            v
     ┌────────────────────┐
     │ ANSI Encoder       │  (Style → ANSI codes)
     └──────┬─────────────┘
            |
            v
      Styled Output
      "\033[34mdef\033[0m \033[32mhello\033[0m():"
```

---

## Module Responsibilities

### 1. `language_registry.py` - Language Catalog

**Purpose**: Maintain catalog of supported languages and detect language from fence hints

**Key Classes**:
- `LanguageSpec`: Metadata for a single language (name, aliases, Pygments lexer)
- `LanguageRegistry`: Central registry with ~20 predefined languages, extensible to 500+

**Responsibilities**:
- Detect language from fence hint (e.g., "python", "py", "python3")
- Provide Pygments lexer name for general languages
- Route data formats (JSON, YAML) to semantic formatter
- Categorize languages (general_purpose, data_format, markup, etc.)

**Extension**: Add new language by adding entry to `LANGUAGES` dict

```python
"elixir": LanguageSpec(
    name="Elixir",
    aliases=["elixir", "ex", "exs"],
    pygments_lexer="elixir",
    category="general_purpose"
)
```

---

### 2. `token_mapper.py` - Token → Semantic Mapping

**Purpose**: Map Pygments tokens to language-agnostic semantic categories

**Key Classes**:
- `TokenMapper`: Converts `Token.Keyword` → `"keyword"`, etc.

**Responsibilities**:
- Map 100+ Pygments token types to ~15 semantic categories
- Handle token hierarchy (e.g., `Token.String.Doc` → `string`)
- Provide fallback for unknown tokens
- Abstract language-specific token differences

**Semantic Categories**:
- `keyword`: Language keywords (def, class, if, etc.)
- `string`: String literals
- `comment`: Comments and docstrings
- `function`: Function/method names
- `class`: Class names
- `number`: Numeric literals
- `operator`: Operators (+, -, etc.)
- `builtin`: Built-in functions
- `literal`: Boolean/null literals
- `variable`: Variable names
- `decorator`: Decorators/annotations
- `escape`: Escape sequences
- `error`: Syntax errors
- `property`: Object properties
- `punctuation`: Brackets, commas, etc.

**Extension**: Add new semantic category by updating `TOKEN_TO_SEMANTIC` dict

---

### 3. `semantic_mapping.py` - Semantic → Theme Mapping

**Purpose**: Map semantic categories to theme color categories

**Key Classes**:
- `SemanticMapping`: Maps `"keyword"` → `"primary"` (theme category)

**Responsibilities**:
- Provide customizable semantic → theme mapping
- Support multiple mapping presets (Claude default, custom themes)
- Enable per-language or per-context overrides
- Decouple syntax categories from theme colors

**Claude Default Mapping**:
```python
{
    "keyword": "primary",      # Blue (keywords stand out)
    "string": "error",         # Red (high visibility)
    "comment": "success",      # Green (lower priority)
    "function": "info",        # Cyan (functions visible)
    "number": "success",       # Green (literals)
    "operator": "metadata",    # Gray (less prominent)
    "builtin": "info",         # Cyan (built-ins)
    # ... etc
}
```

**Extension**: Create custom mapping with `.customize()` method

---

### 4. `structured_formatter.py` - Type-Aware JSON/YAML

**Purpose**: Format structured data (JSON, YAML) with type-based coloring

**Key Classes**:
- `StructuredDataFormatter`: Type-aware formatter for JSON/YAML

**Responsibilities**:
- Parse JSON/YAML into typed elements (keys, values, types)
- Apply type-based coloring:
  - Keys → `metadata` (gray)
  - String values → `success` (green)
  - Numbers → `success` (green)
  - Booleans/null → `info` (cyan)
  - Structural chars (`:`, `{`, `}`) → `metadata` (gray)
- Preserve indentation and formatting
- Handle nested structures

**Why Not Pygments?**: Type-aware coloring provides more semantic information than generic lexer tokens

---

### 5. `highlighter.py` - Orchestration Layer

**Purpose**: Coordinate all components and provide unified public API

**Key Classes**:
- `SyntaxHighlighter`: Main entry point for syntax highlighting

**Responsibilities**:
- Detect Pygments availability
- Route to appropriate formatter (semantic vs. Pygments)
- Initialize sub-components (TokenMapper, StructuredDataFormatter)
- Handle graceful degradation (no Pygments → plain text)
- Provide consistent public API

**Public Methods**:
```python
def highlight(code: str, language_hint: str | None, context: str) -> str:
    """Main highlighting entry point."""
```

---

## Data Flow

### Example 1: Python Code

```python
Input: 'def hello(): print("world")'
Hint: "python"

1. LanguageRegistry.detect("python")
   → LanguageSpec(name="Python", pygments_lexer="python", semantic_formatter=None)

2. Route to Pygments (semantic_formatter is None)

3. Pygments lexer tokenizes:
   [
     (Token.Keyword, "def"),
     (Token.Name.Function, "hello"),
     (Token.Punctuation, "("),
     (Token.Punctuation, ")"),
     ...
   ]

4. TokenMapper.map_token(Token.Keyword)
   → "keyword"

5. SemanticMapping.get_theme_category("keyword")
   → "primary"

6. Theme.get_style("primary")
   → StyleRule(fg_color="blue", bold=False)

7. ANSI Encode
   → "\033[34mdef\033[0m \033[36mhello\033[0m()..."

Output: Styled Python code
```

### Example 2: JSON Data

```python
Input: '{"name": "Alice", "age": 30}'
Hint: "json"

1. LanguageRegistry.detect("json")
   → LanguageSpec(name="JSON", semantic_formatter="json")

2. Route to StructuredDataFormatter (semantic_formatter="json")

3. Parse JSON structure:
   {
     key: "name",
     value: "Alice" (type: string),
     key: "age",
     value: 30 (type: number)
   }

4. Type-based coloring:
   - "name" → metadata (gray)
   - "Alice" → success (green)
   - "age" → metadata (gray)
   - 30 → success (green)

5. Apply styles via theme

Output: Type-colored JSON
```

### Example 3: Unknown Language (Graceful Degradation)

```python
Input: 'code in unknown language'
Hint: "foobar"

1. LanguageRegistry.detect("foobar")
   → None (language not registered)

2. Check Pygments availability
   → False (or True but lexer fails)

3. Return plain text (no highlighting)

Output: 'code in unknown language' (unmodified)
```

---

## Design Decisions

### Why Separate Semantic Mapping from Theme?

**Problem**: Different languages use different token types for similar concepts

**Example**:
- Python: `Token.Keyword` for `def`
- JavaScript: `Token.Keyword` for `function`
- Both should be styled the same color

**Solution**: Introduce semantic layer
```
Python Token.Keyword → "keyword" → "primary" → blue
JS Token.Keyword → "keyword" → "primary" → blue
```

**Benefits**:
- Language-agnostic color consistency
- Easy theme customization (change all keywords by changing "keyword" mapping)
- Decouples token types from visual presentation

---

### Why Use Semantic Formatter for JSON/YAML vs Pygments?

**Pygments Limitation**: Pygments treats JSON as syntax (keys, values, brackets all get token types)

**Our Approach**: Type-aware semantic formatting
- Distinguishes between keys and values
- Colors by data type (string vs number vs boolean)
- Preserves semantic meaning

**Example Comparison**:

```
Pygments: "name": "Alice"
          ^^^^^^  ^^^^^^^
          (both treated as strings, same color)

Semantic: "name": "Alice"
          ^^^^^^  ^^^^^^^
          gray    green
          (key)   (string value)
```

**Benefit**: More semantic information for structured data

---

### Why Token Hierarchy Fallback?

**Problem**: Pygments has hundreds of specialized token types (e.g., `Token.String.Doc`, `Token.Name.Builtin.Pseudo`)

**Solution**: Hierarchical fallback
```python
# Try specific match first
Token.String.Doc → check mapping → "docstring"

# Fall back to parent
Token.String → check mapping → "string"

# Ultimate fallback
None → "text"
```

**Benefits**:
- Handle specialized tokens gracefully
- Maintain reasonable defaults for unmapped tokens
- Reduce mapping table size (don't need entry for every token variant)

---

## Extension Points

### Adding a New Language

**Location**: `language_registry.py → LANGUAGES dict`

```python
"kotlin": LanguageSpec(
    name="Kotlin",
    aliases=["kotlin", "kt"],
    pygments_lexer="kotlin",
    category="general_purpose"
)
```

**Requirements**:
- Pygments must have a lexer for the language
- Choose appropriate category
- List all fence hint aliases

---

### Customizing Syntax Colors

**Per-Category Override**:

```python
from claude_agent_sdk.rendering.syntax import SemanticMapping

# Make all comments dim gray instead of green
custom_mapping = SemanticMapping.claude_default().customize({
    "comment": "metadata"
})

# Apply to theme
theme.semantic_mapping = custom_mapping
```

**Global Theme Override**:

```python
from claude_agent_sdk.rendering import Theme, StyleRule

# Create custom theme with different "metadata" color
theme = Theme.claude_code_default()
theme.metadata = StyleRule(fg_color="bright_black", dim=True)
```

---

### Adding New Semantic Categories

**Step 1**: Update `token_mapper.py`

```python
# Add new token mapping
Token.Name.Annotation: "annotation",  # New category
```

**Step 2**: Update `semantic_mapping.py`

```python
# Map to theme category
"annotation": "warning",  # Yellow/orange
```

**Step 3**: Use in theme

```python
# Theme already has "warning" category
# No changes needed in theme.py
```

---

### Adding Custom Semantic Formatter

For specialized data formats not supported by Pygments:

```python
class TOMLFormatter:
    """Custom formatter for TOML files."""

    def __init__(self, theme, semantic_mapping):
        self.theme = theme
        self.semantic_mapping = semantic_mapping

    def format_toml(self, data: str) -> str:
        """Format TOML with type-based coloring."""
        # Parse TOML
        # Apply type-based colors
        # Return styled string
        pass
```

**Register in Language Registry**:

```python
"toml": LanguageSpec(
    name="TOML",
    aliases=["toml"],
    pygments_lexer="toml",
    category="data_format",
    semantic_formatter="toml"  # Triggers custom formatter
)
```

**Update Highlighter**:

```python
# In highlighter.py
if lang_spec.semantic_formatter == "toml":
    formatter = TOMLFormatter(self.theme, self.semantic_mapping)
    return formatter.format_toml(code)
```

---

## Terminal Compatibility

### Color Depth Detection

The system detects terminal color capabilities and adapts styling accordingly:

**Detection Priority**:
1. `COLORTERM=truecolor` → 24-bit RGB colors
2. `TERM=*-256color` → 256-color palette
3. `TERM=*-color` → 16 basic colors
4. `NO_COLOR=1` → Disable colors

**Graceful Degradation**:
- Truecolor: Full RGB color palette
- 256-color: Map RGB to nearest 256-color index
- 16-color: Map to basic ANSI colors
- Monochrome: Bold/dim/underline only

### ANSI Code Formatting

**Combined Sequences** (Research-Validated):
```
\033[31;1m → Red + Bold
\033[32;3m → Green + Italic
```

**Reset Codes**:
- `\033[0m` → Reset all attributes
- `\033[39m` → Reset foreground color
- `\033[49m` → Reset background color

---

## Performance Considerations

### Token Processing

- **Caching**: TokenMapper creates single mapping dict at initialization
- **Fallback Strategy**: Hierarchical lookup avoids repeated string operations
- **Lazy Import**: Pygments only imported if needed

### Memory Usage

- **Shared Instances**: SemanticMapping and Theme shared across highlighter instances
- **No Token Storage**: Tokens processed in streaming fashion
- **Minimal State**: Highlighter maintains minimal state between calls

---

## Testing Strategy

### Unit Tests

- `test_language_registry.py`: Language detection and lookup
- `test_token_mapper.py`: Token → semantic mapping
- `test_semantic_mapping.py`: Semantic → theme mapping
- `test_structured_formatter.py`: JSON/YAML formatting
- `test_highlighter.py`: Integration tests

### Integration Tests

- End-to-end highlighting for all 20 predefined languages
- Graceful degradation (no Pygments, unknown language)
- Theme customization
- Terminal compatibility modes

---

## Related Documentation

- [API Reference](./api-reference.md) - Public API documentation
- [Extension Guide](./extension-guide.md) - How to extend the system
- [Story 1: Color Analysis](../stories/1-color-analysis.md) - ANSI color mappings
- [Story 4: Unified Syntax](../stories/4-unified-syntax-semantic-highlighting.md) - Implementation details

---

**Document Version**: 1.0
**Last Updated**: 2025-11-09
**Author**: Claude Agent SDK Team
