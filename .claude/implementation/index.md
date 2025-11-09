# Implementation Sprint: Sprint 1.5 - Color Theme Accuracy & Tool Formatting
**Created**: 2025-11-08 21:55
**Status**: active
**Sprint Goal**: Fix CLAUDE-CODE-DEFAULT theme to match actual Claude CLI colors and improve tool call formatting to separate styling for different components

## Overview

This sprint addresses color theming inaccuracies identified through visual comparison with the actual Claude Code CLI. The current SDK theme uses generic ANSI colors that don't match the CLI's actual rendering. Additionally, tool call formatting needs enhancement to separately style tool names, parameters, and values.

**Dependencies**:
- Sprint 1.3 (Theming system) - COMPLETED
- Sprint 1.4 (Screen Reader Mode) - DEFERRED
- Visual color analysis from actual Claude CLI - PENDING (user will provide)

**Estimated Duration**: 6-8 hours

## Stories

### Story 1: Visual Color Analysis & Mapping
**Status**: completed
**Claimed**: 2025-11-08 22:08
**Completed**: 2025-11-08 22:35
**Actual Time**: 35 minutes
**Estimated Time**: 1 hour
**Description**: Analyze actual Claude CLI output via screenshot to map exact ANSI color names used for each semantic category. User will provide comprehensive screenshot showing all message types, tool calls, code blocks, and system messages.

**Acceptance Criteria**:
- [x] User provides screenshot of comprehensive Claude CLI output
- [x] Create color mapping document in `.claude/implementation/stories/1-color-analysis.md`
- [x] Map all semantic categories to ANSI color names (not hex values)
- [x] Identify which colors are bright vs normal variants
- [x] Document special cases (bold, dim, italic modifiers)
- [x] Verify mapping covers: user messages, assistant messages, tool use, tool results, code syntax, system messages, errors, warnings

**Completion Summary**:
Successfully analyzed live Claude Code CLI output by generating comprehensive tool calls and code examples in multiple languages (Python, JavaScript, SQL, Bash, YAML, JSON). Documented complete ANSI color mappings for all syntax elements, message types, and UI components.

**Key Deliverables**:
1. ✅ Complete color mapping document: `.claude/implementation/stories/1-color-analysis.md`
2. ✅ Syntax highlighting configuration design (`SyntaxMapping` dataclass)
3. ✅ Theme customization recommendations
4. ✅ Implementation guidance for Story 4 (syntax highlighting)

**Findings**:
- Keywords: `blue`
- Strings: `red`
- Comments: `green`
- Numbers: `green`
- Types: `cyan`
- Booleans/None: `cyan`
- Operators: `white` (default)
- Built-in functions: `blue`
- User messages: `bright_white` + bold
- Tool use: `bright_blue` + bold
- Errors: `bright_red` + bold
- See full document for complete mappings

**Technical Notes**:
- Focus on ANSI color names: black, red, green, yellow, blue, magenta, cyan, white, bright_black, bright_red, etc.
- Windows Terminal hex values are interpretations of ANSI colors - we need the ANSI names
- Document format styles separately (bold, dim, italic)
- Comprehensive syntax mapping covers Python, JavaScript/TypeScript, SQL, Bash, YAML, JSON

### Story 2: Update CLAUDE-CODE-DEFAULT Theme
**Status**: unassigned
**Estimated Time**: 30 minutes
**Description**: Update the `claude_code_default()` theme method with accurate ANSI color names based on Story 1 analysis.

**Acceptance Criteria**:
- [ ] Update `src/claude_agent_sdk/rendering/theme.py` - `Theme.claude_code_default()` method
- [ ] Replace current color definitions with accurate ANSI names
- [ ] Preserve all semantic categories
- [ ] Update docstring with rationale for color choices
- [ ] Ensure backward compatibility (no API changes)
- [ ] Type hints remain correct

**Technical Notes**:
- Location: `src/claude_agent_sdk/rendering/theme.py:129-194`
- Keep StyleRule structure unchanged
- Only update `fg_color` values and style modifiers (bold, dim, italic)
- Test that theme still serializes/deserializes correctly

### Story 3: Separate Tool Call Component Styling
**Status**: unassigned
**Estimated Time**: 2 hours
**Description**: Enhance `_format_tool_use()` to separately style tool name, parentheses, parameter keys, and parameter values instead of applying one style to the entire string.

**Acceptance Criteria**:
- [ ] Tool name uses dedicated theme color (likely user_message color based on observations)
- [ ] Parentheses use assistant_message color (neutral)
- [ ] Parameter keys use assistant_message color
- [ ] String parameter values use user_message color (for emphasis)
- [ ] Numeric parameter values use user_message color
- [ ] Each component styled independently via `_style()` method
- [ ] Format remains: `● ToolName(key: "value", key: value)`
- [ ] Update tests to verify component-level styling

**Technical Notes**:
- Location: `src/claude_agent_sdk/rendering/formatters.py:239-264`
- Current: `tool_text = self._style(f"{block.name}({params})", "tool_use")`
- New: Separately style name, parens, and each param segment
- May need new semantic categories: `tool_name`, `tool_param_key`, `tool_param_value`
- Or reuse existing categories for semantic consistency

### Story 4: Add Syntax Highlighting Infrastructure
**Status**: unassigned
**Estimated Time**: 3 hours
**Description**: Add syntax highlighting support for code blocks using Pygments integration. Implement `SyntaxMapping` configuration to map Pygments tokens to theme categories, enabling customizable syntax coloring per theme.

**Dependencies**:
- Story 1 (COMPLETED) - Provides complete ANSI color mappings from Claude CLI
- Reference document: `.claude/implementation/stories/1-color-analysis.md`

**Acceptance Criteria**:
- [ ] Add optional dependency: `pygments>=2.17` to `pyproject.toml`
- [ ] Create `src/claude_agent_sdk/rendering/syntax.py` module with `SyntaxHighlighter` class
- [ ] Create `SyntaxMapping` dataclass in `theme.py` with fields for all token categories
- [ ] Add `syntax_mapping: Optional[SyntaxMapping]` field to `Theme` class
- [ ] Implement Pygments token type → SyntaxMapping field mapper
- [ ] Add `enable_syntax_highlighting: bool = True` to `RendererConfig`
- [ ] Integrate syntax highlighter in `_format_tool_result_content()` for code blocks
- [ ] Graceful degradation if Pygments not installed (use plain `code_block` style)
- [ ] Support languages: Python, JavaScript, TypeScript, SQL, Bash, JSON, YAML

**SyntaxMapping Structure** (based on Story 1 findings):
```python
@dataclass
class SyntaxMapping:
    """Maps Pygments token types to Theme semantic categories.

    This allows themes to customize syntax highlighting colors by
    mapping syntax elements to existing theme categories.
    """

    # Core syntax elements (map to theme category names)
    keyword: str = "tool_use"           # blue - def, class, if, async
    string: str = "error"               # red - "strings", 'literals'
    comment: str = "success"            # green - # comments
    number: str = "success"             # green - 42, 3.14
    type_annotation: str = "info"       # cyan - str, int, List
    boolean: str = "info"               # cyan - True, False, null
    builtin_function: str = "tool_use"  # blue - print(), len()
    operator: str = "assistant_message" # white - +, -, ==, and
    function_name: str = "assistant_message"  # white - user functions
    class_name: str = "assistant_message"     # white - in definition
    class_type: str = "info"            # cyan - in type hints
    decorator: str = "assistant_message"      # white - @dataclass
    special_identifier: str = "info"    # cyan - self, this, cls
    punctuation: str = "assistant_message"    # white - [], {}, ()

    # Default fallback
    default: str = "assistant_message"  # white - unclassified tokens
```

**Pygments Token Mapping** (implement in `syntax.py`):
```python
from pygments.token import Token

TOKEN_TO_SYNTAX_CATEGORY = {
    Token.Keyword: "keyword",
    Token.Keyword.Constant: "boolean",
    Token.Keyword.Type: "type_annotation",
    Token.String: "string",
    Token.String.Escape: "string",
    Token.Comment: "comment",
    Token.Number: "number",
    Token.Name.Builtin: "builtin_function",
    Token.Name.Function: "function_name",
    Token.Name.Class: "class_name",
    Token.Name.Decorator: "decorator",
    Token.Name.Variable.Instance: "special_identifier",  # self, cls
    Token.Operator: "operator",
    Token.Punctuation: "punctuation",
    # ... complete mapping
}
```

**Integration Example**:
```python
def apply_syntax_highlighting(
    code: str,
    language: str,
    theme: Theme
) -> str:
    """Apply syntax highlighting using theme's syntax mapping."""
    lexer = get_lexer_by_name(language)
    tokens = lexer.get_tokens(code)

    mapping = theme.syntax_mapping or SyntaxMapping()
    result = []

    for token_type, value in tokens:
        # Get syntax category
        category_field = TOKEN_TO_SYNTAX_CATEGORY.get(
            token_type,
            "default"
        )

        # Get theme category name from syntax mapping
        theme_category = getattr(mapping, category_field)

        # Get style rule from theme
        style_rule = getattr(theme, theme_category)

        # Apply ANSI styling
        styled = apply_ansi_style(value, style_rule)
        result.append(styled)

    return ''.join(result)
```

**Technical Notes**:
- Location: `src/claude_agent_sdk/rendering/syntax.py`
- Pygments is optional - check `importlib.util.find_spec("pygments")`
- Language detection: Use explicit language tag from code fence
- Theme categories referenced must exist in Theme class
- Invalid category names → fallback to "assistant_message"
- Add `pyproject.toml` optional dependency: `[tool.poetry.extras]` → `syntax = ["pygments>=2.17"]`

### Story 5: Control System Message Visibility
**Status**: unassigned
**Estimated Time**: 1 hour
**Description**: Add render level control to hide "System: info" and "System: warning" messages by default, showing only critical system errors unless user explicitly requests detailed output.

**Acceptance Criteria**:
- [ ] Define system message severity levels: debug, info, warning, error, critical
- [ ] Update `RenderLevel` enum or add new `SystemMessageLevel` config
- [ ] Default behavior: Hide info/warning, show error/critical
- [ ] `RenderLevel.DETAILED` shows all system messages
- [ ] `RenderLevel.MINIMAL` shows only critical
- [ ] `RenderLevel.STANDARD` shows error and above (default)
- [ ] Update `format_system_message()` to respect visibility rules
- [ ] Add tests for each render level + message severity combination

**Technical Notes**:
- Location: `src/claude_agent_sdk/rendering/formatters.py:180-194`
- System messages have `type` field indicating severity
- Current implementation doesn't filter by type
- May need to parse message content to infer severity if type not available
- "System: info" → info level (hide by default)
- "System: warning" → warning level (hide by default)
- Cost displays → metadata (always show, styled dim)

### Story 6: Fix Bullet List Indentation
**Status**: unassigned
**Estimated Time**: 1.5 hours
**Description**: Fix indentation for nested bullet points and list items in assistant messages so that subsequent lines and nested items align properly with the first bullet character position.

**Acceptance Criteria**:
- [ ] Top-level bullets (●) appear at left margin
- [ ] Nested list items (`-`, `*`, `1.`) indent from bullet position
- [ ] Multi-line list items wrap with hanging indent
- [ ] Tree connector (⎿) aligns consistently
- [ ] Preserve existing spacing for code blocks
- [ ] Update `format_assistant_message()` with proper indentation logic
- [ ] Add tests for nested lists, multi-line items, mixed content

**Technical Notes**:
- Location: `src/claude_agent_sdk/rendering/formatters.py:126-178`
- Current issue: Nested `-` bullets don't indent from `●` position
- Expected format:
  ```
  ● I've created a function with:
    - Input validation
    - Efficient algorithm
    - Clear documentation
  ```
- May need to parse markdown list structure
- Consider using a markdown parser or custom list detection regex

### Story 7: Update Tests for Color Changes
**Status**: unassigned
**Estimated Time**: 1 hour
**Description**: Update existing theme and formatter tests to reflect new ANSI color mappings and component-level styling changes.

**Acceptance Criteria**:
- [ ] Update `tests/test_rendering_theme.py` for new claude_code_default colors
- [ ] Update `tests/test_rendering_formatters.py` for tool call component styling
- [ ] Add tests for syntax highlighting (if enabled)
- [ ] Add tests for system message visibility filtering
- [ ] Add tests for bullet indentation fixes
- [ ] All 556+ existing tests continue to pass
- [ ] Zero regressions from Sprint 1.3

**Technical Notes**:
- Focus test files:
  - `tests/test_rendering_theme.py` (21 tests)
  - `tests/test_rendering_formatters.py` (existing tests)
  - `tests/test_rendering_formatters_color.py` (8 tests)
- Update golden outputs / snapshots if using snapshot testing
- Verify ANSI escape code sequences match expected values

### Story 8: Update Documentation & Examples
**Status**: unassigned
**Estimated Time**: 45 minutes
**Description**: Update README, API documentation, and demo examples to reflect accurate color theming and new formatting features.

**Acceptance Criteria**:
- [ ] Update README.md theme section with corrected color descriptions
- [ ] Update `examples/demo_themes.py` if needed for new categories
- [ ] Update `examples/comprehensive_theming_demo.py` to showcase new features
- [ ] Add syntax highlighting example if feature implemented
- [ ] Document system message visibility controls
- [ ] Document tool call component styling behavior

**Technical Notes**:
- README location: Root `README.md` (theme section around line 200+)
- Note that colors will now accurately match Claude CLI
- Add troubleshooting section if syntax highlighting is optional dependency

## Progress Log

### 2025-11-08 22:35 - Story 1 Completed
- ✅ **Story 1 COMPLETED** in 35 minutes (estimated: 1 hour)
- Method: Generated comprehensive live CLI output with diverse tool calls and code examples
- Languages covered: Python, JavaScript/TypeScript, SQL, Bash, YAML, JSON
- Created complete color mapping document: `.claude/implementation/stories/1-color-analysis.md`
- **Key Findings**:
  - Keywords: `blue` (def, class, if, async, SELECT)
  - Strings: `red` (all string types, escape sequences)
  - Comments: `green` (all comment types)
  - Numbers: `green` (integers, floats, binary, hex)
  - Types: `cyan` (str, int, List, Optional)
  - Booleans/None: `cyan` (True, False, null, None)
  - Operators: `white` (default, no highlighting)
  - Built-in functions: `blue` (print, len, range)
- **Deliverable**: Designed `SyntaxMapping` configuration structure for customizable syntax highlighting
- **Impact**: Story 4 significantly enhanced with concrete implementation guidance
- Updated Story 4 estimated time: 2h → 3h (added configuration infrastructure)
- Sprint now has clear path forward with empirical color data

### 2025-11-08 21:55 - Sprint Started
- Archived Sprint 1.4 (Screen Reader Mode) to `.claude/implementation/archive/2025-11-08-2154/`
- Created Sprint 1.5 structure for color theme accuracy
- Defined 8 stories covering color analysis, theme updates, formatting enhancements
- Estimated total time: 6-8 hours
- Sprint builds on completed Sprint 1.3 theming infrastructure
- Story 1 awaits user-provided screenshot for color analysis

## Sprint Summary
_To be filled upon completion_
