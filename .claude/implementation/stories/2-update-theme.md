# Story 2: Update CLAUDE-CODE-DEFAULT Theme

**Status**: unassigned
**Assignee**: unassigned
**Estimated Time**: 30 minutes
**Actual Time**: TBD

---

## Dependencies

- Story 1 (COMPLETED) - Provides accurate ANSI color mappings
- Reference: `.claude/implementation/stories/1-color-analysis.md`

---

## Description

Update the `claude_code_default()` theme method in `theme.py` with accurate ANSI color names based on Story 1's comprehensive color analysis. The current theme uses generic/assumed colors that don't match Claude CLI's actual rendering.

**Goal**: Achieve pixel-perfect color matching with Claude Code CLI for all semantic categories.

---

## Acceptance Criteria

- [ ] Update `src/claude_agent_sdk/rendering/theme.py` - `Theme.claude_code_default()` method
- [ ] Replace current color definitions with accurate ANSI names from Story 1
- [ ] Preserve all existing semantic categories (no removals)
- [ ] Update docstring with rationale for color choices (reference Story 1)
- [ ] Ensure backward compatibility (no API changes)
- [ ] Type hints remain correct
- [ ] Theme serializes/deserializes correctly
- [ ] Manual validation against live Claude CLI output

---

## Technical Implementation

### Affected Files

**Primary**:
- `src/claude_agent_sdk/rendering/theme.py:127-193` - `claude_code_default()` method

**Validation**:
- Manual comparison with Claude CLI output
- Existing tests in `tests/test_rendering_theme.py`

### Current Implementation

```python
@classmethod
def claude_code_default(cls) -> Theme:
    """Create the default Claude Code CLI theme."""
    return cls(
        # Message types
        user_message=StyleRule(fg_color="bright_white", bold=True),
        assistant_message=StyleRule(fg_color="white"),
        system_message=StyleRule(fg_color="bright_black", dim=True),

        # Tool-related
        tool_use=StyleRule(fg_color="bright_blue", bold=True),
        tool_result=StyleRule(fg_color="blue"),
        tool_error=StyleRule(fg_color="bright_red", bold=True),

        # ... rest of categories
    )
```

### Required Changes

Based on Story 1 findings, **NO CHANGES REQUIRED** to color values - the current theme already matches Claude CLI exactly! However, we should:

1. **Enhance docstring** to reference Story 1 analysis
2. **Add validation comments** for each color choice
3. **Document the empirical verification**

### Updated Implementation

```python
@classmethod
def claude_code_default(cls) -> Theme:
    """Create the default Claude Code CLI theme.

    This theme accurately replicates the Claude Code CLI rendering,
    validated through empirical analysis (Sprint 1.5, Story 1).

    Color Mappings (verified 2025-11-08):
    - All colors match Claude CLI's actual ANSI output
    - Syntax highlighting matches observed behavior
    - UI elements match renderer color patterns

    For complete color analysis, see:
    `.claude/implementation/stories/1-color-analysis.md`

    Design Principles:
    - Semantic color usage (blue=keywords, red=strings, green=comments/numbers)
    - High contrast for user input vs. assistant content
    - Accessibility (color + style cues like bold/dim)
    - Cross-language consistency

    Syntax Highlighting Notes:
    When used with SyntaxMapping (Story 4), this theme provides:
    - Keywords: blue (via tool_use → bright_blue)
    - Strings: red (via error → bright_red)
    - Comments: green (via success → bright_green)
    - Numbers: green (via success → bright_green)
    - Types: cyan (via info → bright_cyan)

    Returns:
        Theme configured with Claude CLI-accurate colors

    See Also:
        - Story 1 color analysis document
        - `Theme.syntax_mapping` for code highlighting configuration
    """
    return cls(
        # Message types - validated against Claude CLI
        user_message=StyleRule(fg_color="bright_white", bold=True),  # High visibility
        assistant_message=StyleRule(fg_color="white"),                # Clear default
        system_message=StyleRule(fg_color="bright_black", dim=True), # De-emphasized

        # Tool-related - blue family for actions
        tool_use=StyleRule(fg_color="bright_blue", bold=True),  # Commands/actions
        tool_result=StyleRule(fg_color="blue"),                 # Results (less prominent)
        tool_error=StyleRule(fg_color="bright_red", bold=True), # Critical errors

        # Semantic categories - standard conventions
        error=StyleRule(fg_color="bright_red", bold=True),    # Red = errors
        warning=StyleRule(fg_color="bright_yellow", bold=True), # Yellow = warnings
        success=StyleRule(fg_color="bright_green", bold=True),  # Green = success
        info=StyleRule(fg_color="bright_cyan"),                 # Cyan = info
        debug=StyleRule(fg_color="bright_black", dim=True),     # Gray = debug

        # UI elements - subtle, non-distracting
        bullet=StyleRule(fg_color="bright_black", dim=True),         # Metadata bullets
        tree_connector=StyleRule(fg_color="bright_black", dim=True), # Tree structure
        metadata=StyleRule(fg_color="bright_black", dim=True),       # Timestamps, sizes
        truncation=StyleRule(fg_color="bright_black", dim=True, italic=True), # Truncation markers

        # Code elements - distinct but readable
        code_block=StyleRule(fg_color="cyan"),        # Multi-line code
        inline_code=StyleRule(fg_color="bright_cyan"), # Inline `code`

        # Special
        thinking=StyleRule(fg_color="magenta", italic=True),    # Reasoning
        cost_display=StyleRule(fg_color="bright_black", dim=True), # Cost info
    )
```

### Validation Notes

All current colors are **correct** per Story 1 analysis. The main enhancement is **documentation** rather than color changes.

**Note for Future Stories**:
- Story 9 (Pattern Detection) may need additional semantic categories for technical references
- Story 10 (Structured Data) may need JSON/YAML-specific categories
- Consider adding these in future iterations

---

## Testing Strategy

### Manual Validation

1. **Visual Comparison**:
   - Run SDK with updated theme
   - Compare output side-by-side with Claude CLI
   - Verify each semantic category matches

2. **Test Cases**:
   ```python
   # Test all message types
   messages = [
       UserMessage(content=[TextBlock(text="User input")]),
       AssistantMessage(content=[TextBlock(text="Assistant response")]),
       SystemMessage(content=[TextBlock(text="System: info - Message")]),
   ]

   # Test all semantic categories
   formatted = renderer.format_message(AssistantMessage(content=[
       TextBlock(text="✅ Success message"),
       TextBlock(text="⚠️ Warning message"),
       TextBlock(text="❌ Error message"),
       TextBlock(text="ℹ️ Info message"),
   ]))
   ```

### Unit Tests

Existing tests in `tests/test_rendering_theme.py` should pass without modification:
- ✅ `test_claude_code_default_theme_creation`
- ✅ `test_theme_serialization`
- ✅ `test_theme_deserialization`
- ✅ `test_all_categories_have_style_rules`

No new tests required unless adding new semantic categories.

---

## Implementation Guidance

### Architecture Reference

- See: `stories/renderer-architecture.md` - Section: "Theme Mapper"
- Theme provides semantic category → ANSI color mappings
- Renderer applies theme styles to classified content

### Integration Pattern

```python
# How renderer uses theme
style_rule = theme.tool_use  # Get style for category
ansi_code = apply_ansi_style(text, style_rule)  # Apply ANSI formatting
```

### Code Examples

**Testing theme in isolation**:
```python
from claude_agent_sdk.rendering.theme import Theme

theme = Theme.claude_code_default()
print(f"User message color: {theme.user_message.fg_color}")
print(f"Tool use color: {theme.tool_use.fg_color}")
# Verify all colors match Story 1 mappings
```

**Comparing with other themes**:
```python
default_theme = Theme.claude_code_default()
solarized = Theme.solarized_dark()

# Compare semantic mappings
print(f"Default tool_use: {default_theme.tool_use.fg_color}")
print(f"Solarized tool_use: {solarized.tool_use.fg_color}")
```

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking user customizations | High | Low | Colors unchanged, only docs updated |
| Test failures | Medium | Low | Existing tests designed for current colors |
| Missing semantic categories | Medium | Medium | Plan for future additions in Stories 9-10 |

---

## Follow-Up Tasks

After completing this story:

1. **Story 3** can proceed with component-level styling using accurate theme colors
2. **Story 4** can implement SyntaxMapping using verified theme categories
3. **Story 9** may identify need for new semantic categories (e.g., `technical_reference`)

---

## Completion Checklist

- [ ] Docstring updated with Story 1 reference
- [ ] Validation comments added for each color choice
- [ ] Manual visual comparison with Claude CLI performed
- [ ] All existing theme tests passing
- [ ] Code reviewed
- [ ] Story marked complete in index.md

---

**Document Version**: 1.0
**Created**: 2025-11-08 22:55
**Author**: Claude Agent SDK Team
