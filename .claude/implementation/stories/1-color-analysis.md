# Story 1: Visual Color Analysis & Mapping

**Date**: 2025-11-08
**Status**: Completed
**Completion Time**: 22:35
**Method**: Live Claude Code CLI output analysis

---

## Executive Summary

Comprehensive color analysis completed via live Claude Code CLI session. All syntax elements, message types, and UI components have been mapped to ANSI color codes. This document serves as the authoritative reference for implementing accurate Claude Code theming.

---

## Methodology

**Approach**: Generated diverse tool calls, code examples, and structured outputs in an active Claude Code CLI session to observe actual rendering behavior.

**Coverage**:
- ✅ All message types (user, assistant, system, tool use, tool results, errors)
- ✅ All syntax elements (keywords, strings, comments, numbers, operators, types)
- ✅ Multiple programming languages (Python, JavaScript/TypeScript, SQL, Bash, YAML, JSON)
- ✅ Special formatting (thinking blocks, code blocks, inline code, metadata)
- ✅ UI elements (bullets, tree connectors, truncation indicators)

---

## Complete ANSI Color Mappings

### Message Type Categories

| Category | ANSI Color | Modifiers | Usage |
|----------|-----------|-----------|-------|
| **User Message** | `bright_white` | `bold` | User input messages |
| **Assistant Message** | `white` | none | Assistant text responses |
| **System Message** | `bright_black` | `dim` | System notifications, metadata |
| **Tool Use** | `bright_blue` | `bold` | Tool invocation headers |
| **Tool Result** | `blue` | none | Successful tool result content |
| **Tool Error** | `bright_red` | `bold` | Failed tool results |
| **Thinking Block** | `magenta` | `italic` | Assistant reasoning (when shown) |

### Code Syntax Categories

#### Keywords & Control Flow
**Color**: `blue`
**Elements**:
- Language keywords: `import`, `from`, `def`, `return`, `class`, `async`, `await`
- Control flow: `if`, `else`, `elif`, `while`, `for`, `break`, `continue`
- Exception handling: `try`, `except`, `finally`, `raise`, `catch`, `throw`
- Function/class declarations: `function`, `const`, `let`, `var`, `static`, `public`, `private`
- Special keywords: `yield`, `lambda`, `new`, `this`, `self`, `with`, `as`
- SQL keywords: `SELECT`, `FROM`, `WHERE`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `TABLE`, `JOIN`, `GROUP BY`, `ORDER BY`

#### Strings & Literals
**Color**: `red`
**Elements**:
- All string types: single quotes `'...'`, double quotes `"..."`, triple quotes `"""..."""`
- Template literals: `` `...${var}...` ``
- f-strings: `f"...{var}..."`
- Raw strings: `r"..."`
- Regular expressions: `/pattern/flags`, `r'pattern'`
- Escape sequences within strings: `\n`, `\t`, `\r`, `\\`, `\"`, `\'`, `\u2713`

#### Comments
**Color**: `green`
**Elements**:
- Python: `# comment`
- JavaScript/C-style: `// comment`, `/* comment */`
- SQL: `-- comment`
- Docstrings: `"""Documentation"""`, `/** JSDoc */`

#### Numbers
**Color**: `green`
**Elements**:
- Integers: `0`, `1`, `42`, `1000`
- Floats: `3.14`, `0.5`, `100.0`
- Scientific notation: `1e10`, `2.5e-3`
- Binary: `0b1010`, `0b1100`
- Hexadecimal: `0xFF`, `0x1A2B`
- Octal: `0o755`

#### Types & Type Annotations
**Color**: `cyan`
**Elements**:
- Built-in types: `str`, `int`, `float`, `bool`, `list`, `dict`, `tuple`, `set`
- Generic types: `List`, `Dict`, `Optional`, `Union`, `Tuple`, `Set`
- Advanced types: `TypeVar`, `Generic`, `Protocol`, `Callable`, `Awaitable`
- JavaScript types: `string`, `number`, `boolean`, `Promise`, `Array`
- SQL types: `INTEGER`, `VARCHAR`, `BOOLEAN`, `TIMESTAMP`, `TEXT`

#### Booleans & Special Values
**Color**: `cyan`
**Elements**:
- Python: `True`, `False`, `None`
- JavaScript: `true`, `false`, `null`, `undefined`
- SQL: `TRUE`, `FALSE`, `NULL`

#### Operators
**Color**: `white` (default, no highlighting)
**Elements**:
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `**`, `//`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`, `===`, `!==`
- Logical: `and`, `or`, `not`, `&&`, `||`, `!`
- Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`
- Bitwise: `&`, `|`, `^`, `~`, `<<`, `>>`, `>>>`
- Membership: `in`, `not in`
- Identity: `is`, `is not`
- Ternary: `?`, `:`

#### Functions & Methods
**Color**: `white` (default)
**Special built-ins**: `blue`

**Elements**:
- User-defined functions: white (e.g., `process_user_input()`)
- Built-in functions: `blue` (e.g., `print()`, `len()`, `range()`, `map()`, `filter()`, `sorted()`)
- Methods: white (e.g., `.read()`, `.execute()`, `.format()`)

#### Class & Object Elements
**Color**: Mixed

**Breakdown**:
- `class` keyword: `blue`
- Class name in definition: `white`
- Class name in type hints: `cyan` (e.g., `-> User`)
- Decorators: `white` (e.g., `@dataclass`, `@property`)
- Magic methods: `white` (e.g., `__init__`, `__repr__`)
- `self` / `cls` / `this`: `cyan`

#### Punctuation & Delimiters
**Color**: `white` (default)
**Elements**:
- Brackets: `[]`, `{}`, `()`
- Separators: `,`, `;`, `:`, `.`
- String delimiters: `'`, `"`, `` ` ``

#### SQL-Specific Syntax
**Color**: Mixed

**Keywords** (`blue`):
- DDL: `CREATE`, `ALTER`, `DROP`, `TABLE`, `INDEX`
- DML: `INSERT`, `UPDATE`, `DELETE`, `INTO`, `VALUES`, `SET`
- DQL: `SELECT`, `FROM`, `WHERE`, `JOIN`, `LEFT`, `RIGHT`, `INNER`
- Clauses: `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`, `OFFSET`
- Functions: `COUNT`, `SUM`, `AVG`, `MAX`, `MIN`
- Conditionals: `CASE`, `WHEN`, `THEN`, `ELSE`, `END`

**Types & Constraints** (`cyan`):
- `INTEGER`, `VARCHAR`, `TEXT`, `BOOLEAN`, `TIMESTAMP`, `DATE`
- `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE`, `DEFAULT`
- `AUTOINCREMENT`, `AUTO_INCREMENT`
- `CURRENT_TIMESTAMP`

#### YAML-Specific Syntax
**Color**: Mixed

**Elements**:
- Keys/properties: `blue` (before `:`)
- String values: `red`
- Boolean/null: `cyan` (`true`, `false`, `null`)
- Numeric values: `green`
- Comments: `green` (`# comment`)
- Anchors/aliases: `bright_black` dim (`&anchor`, `*alias`, `<<:`)

### UI & Formatting Elements

| Element | ANSI Color | Modifiers | Usage |
|---------|-----------|-----------|-------|
| **Code Block** | `cyan` | none | Multi-line code fence content |
| **Inline Code** | `bright_cyan` | none | Backtick-wrapped `code` |
| **Bullet** | `bright_black` | `dim` | List bullets (●) |
| **Tree Connector** | `bright_black` | `dim` | Tree lines (⎿) |
| **Metadata** | `bright_black` | `dim` | Timestamps, sizes, counts |
| **Truncation** | `bright_black` | `dim`, `italic` | `... (truncated)` |
| **Cost Display** | `bright_black` | `dim` | Token usage, API costs |

### Semantic Message Formatting

| Category | ANSI Color | Modifiers | Usage |
|----------|-----------|-----------|-------|
| **Error** | `bright_red` | `bold` | ❌ ERROR messages |
| **Warning** | `bright_yellow` | `bold` | ⚠️ WARNING messages |
| **Success** | `bright_green` | `bold` | ✅ SUCCESS messages |
| **Info** | `bright_cyan` | none | ℹ️ INFO messages |
| **Debug** | `bright_black` | `dim` | Debug output |

---

## Context-Specific Color Rules

### Comment Annotations

When comments contain special labels, those labels may receive semantic highlighting:

- `# WARNING: ...` → `bright_yellow` for "WARNING"
- `# ERROR: ...` → `bright_red` for "ERROR"
- `# TODO: ...` → `bright_cyan` for "TODO"
- `# FIXME: ...` → `bright_yellow` for "FIXME"

### String Content

The base string color is `red`, but escape sequences within strings remain `red` (same color, not highlighted separately).

---

## Design Principles Observed

### 1. Semantic Consistency
Colors follow semantic meaning across languages:
- `blue` = keywords, actions, commands
- `red` = data (strings, literals)
- `green` = comments, numbers
- `cyan` = types, special identifiers

### 2. Contrast & Hierarchy
- User input: Brightest (`bright_white` + `bold`)
- Assistant content: Clear default (`white`)
- Metadata: Subdued (`bright_black` + `dim`)

### 3. Accessibility
- Colors paired with style modifiers (bold, dim, italic)
- High contrast for critical elements (errors, warnings)
- Graceful degradation for limited color terminals

### 4. Cross-Language Consistency
Same syntax roles receive same colors across Python, JavaScript, SQL, etc.:
- Keywords always `blue`
- Strings always `red`
- Types always `cyan`

---

## Implementation Recommendations

### 1. Syntax Highlighting Configuration

Create a new `SyntaxMapping` configuration structure:

```python
@dataclass
class SyntaxMapping:
    """Maps syntax token types to theme categories."""

    # Token categories
    keyword: str = "tool_use"           # Maps to blue
    string: str = "error"               # Maps to red
    comment: str = "success"            # Maps to green
    number: str = "success"             # Maps to green
    type_annotation: str = "info"       # Maps to cyan
    boolean: str = "info"               # Maps to cyan
    builtin: str = "tool_use"           # Maps to blue (print, len, etc)
    operator: str = "assistant_message" # Maps to white
    function: str = "assistant_message" # Maps to white
    class_name: str = "assistant_message" # Maps to white (definition)
    class_type: str = "info"            # Maps to cyan (type hint)
    decorator: str = "assistant_message" # Maps to white
    special_identifier: str = "info"    # Maps to cyan (self, this, cls)
```

### 2. Theme Integration

Update `Theme` class to include optional syntax mapping:

```python
@dataclass
class Theme:
    # ... existing fields ...

    # Optional syntax highlighting configuration
    syntax_mapping: Optional[SyntaxMapping] = None

    @classmethod
    def claude_code_default(cls) -> Theme:
        return cls(
            # ... existing style rules ...
            syntax_mapping=SyntaxMapping()  # Use defaults
        )
```

### 3. Custom Theme Example

```python
# User creates custom theme with different syntax colors
custom_theme = Theme(
    # Message types
    user_message=StyleRule(fg_color="bright_cyan", bold=True),
    assistant_message=StyleRule(fg_color="white"),

    # ... other categories ...

    # Custom syntax mapping
    syntax_mapping=SyntaxMapping(
        keyword="warning",        # Yellow keywords instead of blue
        string="success",         # Green strings instead of red
        comment="debug",          # Dim comments
        number="info",            # Cyan numbers
    )
)
```

### 4. Syntax Highlighter Integration

Reference implementation approach (Story 4):

```python
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

# Map Pygments token types to SyntaxMapping fields
TOKEN_MAPPING = {
    Token.Keyword: "keyword",
    Token.String: "string",
    Token.Comment: "comment",
    Token.Number: "number",
    Token.Name.Builtin: "builtin",
    # ... complete mapping
}

def apply_syntax_highlighting(code: str, language: str, theme: Theme) -> str:
    """Apply syntax highlighting using theme's syntax mapping."""
    lexer = get_lexer_by_name(language)
    tokens = lexer.get_tokens(code)

    result = []
    for token_type, value in tokens:
        # Get syntax category from mapping
        category = TOKEN_MAPPING.get(token_type, "assistant_message")

        # Get theme category from syntax mapping
        if theme.syntax_mapping:
            theme_category = getattr(theme.syntax_mapping, category)
        else:
            theme_category = "assistant_message"

        # Apply style
        styled_value = theme.apply_style(value, theme_category)
        result.append(styled_value)

    return ''.join(result)
```

---

## Validation & Testing

### Manual Validation Completed
- ✅ Python syntax (all elements covered)
- ✅ JavaScript/TypeScript syntax
- ✅ SQL syntax
- ✅ Bash scripts
- ✅ YAML configuration
- ✅ JSON data
- ✅ Regular expressions
- ✅ Template strings and f-strings

### Test Coverage Needed
- [ ] Unit tests for `SyntaxMapping` serialization/deserialization
- [ ] Integration tests with Pygments token mapping
- [ ] Visual regression tests for theme consistency
- [ ] Accessibility tests for color contrast ratios

---

## Reference Materials

### ANSI Color Code Reference

**Standard Colors (30-37 foreground)**:
- 30 = Black
- 31 = Red
- 32 = Green
- 33 = Yellow
- 34 = Blue
- 35 = Magenta
- 36 = Cyan
- 37 = White

**Bright Colors (90-97 foreground)**:
- 90 = Bright Black (Gray)
- 91 = Bright Red
- 92 = Bright Green
- 93 = Bright Yellow
- 94 = Bright Blue
- 95 = Bright Magenta
- 96 = Bright Cyan
- 97 = Bright White

**Style Modifiers**:
- 1 = Bold
- 2 = Dim
- 3 = Italic
- 4 = Underline
- 0 = Reset

### Escape Sequence Format
```
ESC[<style>;<color>m<text>ESC[0m

Example:
ESC[1;94m  # Bold + Bright Blue
ESC[2;90m  # Dim + Bright Black
ESC[3;35m  # Italic + Magenta
```

---

## Story 1 Completion Summary

**Status**: ✅ Completed
**Time Invested**: ~35 minutes
**Method**: Live CLI output analysis
**Deliverables**:
1. ✅ Complete ANSI color mapping document (this file)
2. ✅ Syntax highlighting design recommendations
3. ✅ Theme customization structure proposal
4. ✅ Implementation guidance for Story 4

**Next Steps**:
- Story 2: Update `claude_code_default()` theme (confirm colors match)
- Story 4: Implement syntax highlighting infrastructure
- Story 7: Create comprehensive test coverage

---

## Appendix A: Quick Reference Table

| Syntax Element | Color | Example |
|----------------|-------|---------|
| Keyword | `blue` | `def`, `class`, `if`, `async` |
| String | `red` | `"hello"`, `'world'`, `f"{var}"` |
| Comment | `green` | `# comment`, `// comment` |
| Number | `green` | `42`, `3.14`, `0xFF` |
| Type | `cyan` | `str`, `int`, `List[str]` |
| Boolean | `cyan` | `True`, `False`, `null` |
| Built-in | `blue` | `print()`, `len()`, `range()` |
| Operator | `white` | `+`, `==`, `and`, `=>` |
| Function | `white` | `my_function()` |
| Self/This | `cyan` | `self`, `this`, `cls` |

## Appendix B: Diff/Update Tool Color Mappings

### Diff Output ANSI Colors

The Edit/Update tool uses background colors for diff indicators while attempting to preserve foreground syntax highlighting where readable.

#### Diff Indicators (Background Colors)

| Element | Background | Foreground | Prefix | Usage |
|---------|-----------|------------|--------|-------|
| **Removed Lines** | `red` | `white`/bright | `-` | Deleted content |
| **Added Lines** | `green` | `white`/bright | `+` | Inserted content |
| **Context Lines** | none (default) | `white` | (none) | Unchanged lines |
| **Inline Changes (removed)** | `dark red` | `white` | (none) | Changed portion within line |
| **Inline Changes (added)** | `dark green` | `white` | (none) | Changed portion within line |

#### Diff Metadata

| Element | Color | Example |
|---------|-------|---------|
| **File Operation Header** | `green` | `● Update(.claude\implementation\index.md)` |
| **Line Numbers** | `white` (default) | Left margin numbers |
| **Summary Line** | `white` | `Updated <file> with X additions and Y removals` |

#### Syntax Highlighting Within Diffs

The diff tool attempts to preserve some syntax highlighting on colored backgrounds:

- **Markdown headers** (`##`, `###`) - Bright white on backgrounds
- **Status keywords** - `error` → red, `completed` → green (even on diff backgrounds)
- **File paths** - Red or cyan (e.g., `.claude/...`)
- **Checkboxes** - `[x]`, `[ ]` in white
- **Checkmarks** - `✅` in green

**Note**: Background colors take precedence for readability. Foreground syntax highlighting is applied only where it doesn't conflict with diff comprehension.

---

**Document Version**: 1.1
**Last Updated**: 2025-11-08 22:40
**Author**: Claude Agent SDK Team
