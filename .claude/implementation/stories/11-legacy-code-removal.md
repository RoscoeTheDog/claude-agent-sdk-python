# Story 11: Legacy Code Removal & Cleanup

**Status**: unassigned
**Assignee**: unassigned
**Estimated Time**: 1 hour
**Actual Time**: TBD
**Priority**: MEDIUM
**Dependencies**: Story 4 (must be completed and tested first)

---

## Description

Remove redundant legacy code that conflicts with the new modular syntax highlighting architecture. This story ensures a clean codebase with no duplicate or obsolete implementations.

**Goal**: Eliminate technical debt and ensure single source of truth for all syntax highlighting functionality.

---

## Acceptance Criteria

### Code Removal
- [ ] Identify any pre-existing syntax highlighting code in `rendering/` module
- [ ] Remove duplicate token mapping logic (if exists)
- [ ] Remove any hard-coded syntax coloring (if exists)
- [ ] Remove obsolete theme fields related to old syntax approach (if exists)

### Configuration Cleanup
- [ ] Remove deprecated configuration options (if any)
- [ ] Ensure no conflicting `enable_syntax_*` flags exist
- [ ] Consolidate to single `enable_syntax_highlighting` flag from Story 4

### Import Cleanup
- [ ] Update imports to use new `syntax/` module
- [ ] Remove imports of deprecated/removed modules
- [ ] Verify no circular dependencies

### Test Cleanup
- [ ] Remove or update tests for removed code
- [ ] Ensure no test failures from removed functionality
- [ ] Verify new tests from Story 4 provide equivalent coverage

---

## Investigation Checklist

Run these checks to find legacy code:

```bash
# Search for potential legacy syntax highlighting
grep -r "syntax" src/claude_agent_sdk/rendering/*.py | grep -v "syntax/"

# Search for hard-coded color assignments in code formatting
grep -r "ANSI\|\\x1b\[" src/claude_agent_sdk/rendering/*.py

# Search for duplicate token/lexer references
grep -r "pygments\|lexer\|token" src/claude_agent_sdk/rendering/*.py | grep -v "syntax/"

# Find obsolete theme fields
grep -r "SyntaxMapping" src/claude_agent_sdk/rendering/theme.py
```

---

## Removal Targets

### Potential Legacy Locations

Based on typical SDK structure, check these areas:

1. **`formatters.py`**: Any inline syntax coloring logic
2. **`theme.py`**: Old `SyntaxMapping` dataclass (replaced by `semantic_mapping.py`)
3. **`config.py`**: Multiple syntax-related flags (consolidate to one)
4. **Tests**: Old syntax highlighting tests

### Example Removals

**If found - Remove**:

```python
# OLD: Hard-coded token mapping in theme.py
@dataclass
class SyntaxMapping:  # DELETE - replaced by syntax/semantic_mapping.py
    keyword: str = "tool_use"
    string: str = "error"
    # ...

# OLD: Inline syntax coloring in formatters.py
def _highlight_python(code: str):  # DELETE - replaced by SyntaxHighlighter
    # Hard-coded Python highlighting logic
    pass

# OLD: Multiple flags in config.py
@dataclass
class RendererConfig:
    enable_code_highlighting: bool = True  # DELETE
    enable_json_formatting: bool = True    # DELETE
    # Replace with single: enable_syntax_highlighting: bool = True
```

**Keep (from Story 4)**:

```python
# KEEP: New modular architecture
from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

# KEEP: Single consolidated flag
@dataclass
class RendererConfig:
    enable_syntax_highlighting: bool = True  # KEEP - from Story 4
```

---

## Safe Removal Process

### Step 1: Backup

Before removing any code:

```bash
# Create backup branch
git checkout -b backup/pre-story-11-cleanup
git commit -am "Backup before Story 11 cleanup"
git checkout <your-working-branch>
```

### Step 2: Identify Dependencies

For each piece of code to remove:

1. Search for references: `grep -r "function_name" src/`
2. Check test usage: `grep -r "function_name" tests/`
3. Document in removal plan

### Step 3: Remove Incrementally

Remove one component at a time, running tests after each:

```bash
# Remove component
# Edit file, delete old code

# Run tests
python -m pytest tests/

# If tests pass, commit
git add .
git commit -m "Remove legacy [component_name]"

# If tests fail, investigate and fix
```

### Step 4: Verify Integration

After all removals:

```bash
# Full test suite
python -m pytest tests/

# Type checking
python -m mypy src/

# Linting
python -m ruff check src/ tests/
```

---

## Documentation Updates

Update these docs to reflect removals:

- [ ] Update `README.md` if syntax highlighting usage changed
- [ ] Update docstrings in affected modules
- [ ] Update migration guide (if users relied on removed APIs)

---

## Testing Strategy

### Regression Tests

Ensure Story 4 functionality still works:

```python
def test_syntax_highlighting_still_works():
    """Verify new architecture works after legacy removal."""
    theme = Theme.claude_code_default()
    highlighter = SyntaxHighlighter(theme)

    code = 'def hello(): print("world")'
    result = highlighter.highlight(code, language_hint="python")

    assert 'def' in result
    assert '\x1b[' in result  # Has ANSI codes

def test_no_duplicate_highlighting():
    """Ensure code isn't highlighted twice (old + new)."""
    # Test that output doesn't contain nested ANSI codes
    # or duplicate coloring
    pass
```

### Integration Tests

Verify end-to-end rendering:

```python
def test_full_message_rendering():
    """Test complete message with code blocks after cleanup."""
    config = RendererConfig(
        theme=Theme.claude_code_default(),
        enable_syntax_highlighting=True
    )
    formatter = MessageFormatter(config)

    message = AssistantMessage(content=[
        TextBlock(text="```python\ndef test(): pass\n```")
    ])

    rendered = formatter.format_message(message)

    # Should have syntax highlighting
    assert 'def' in rendered
    # Should not have double-encoding or errors
    assert rendered.count('\x1b[') > 0  # Has ANSI codes
```

---

## Rollback Plan

If issues discovered after removal:

1. **Immediate rollback**:
   ```bash
   git revert <commit-hash>
   ```

2. **Investigate issue**:
   - What broke?
   - Was removed code still in use?
   - Missing test coverage?

3. **Fix properly**:
   - If code was needed, restore and refactor to use new architecture
   - If test gap, add tests
   - If documentation gap, update docs

---

## Completion Checklist

- [ ] Investigated codebase for legacy syntax code
- [ ] Documented all code targeted for removal
- [ ] Created backup branch
- [ ] Removed legacy code incrementally with tests
- [ ] Updated imports and references
- [ ] Removed obsolete tests or updated to new architecture
- [ ] Full test suite passing
- [ ] Type checking passing
- [ ] Linting passing
- [ ] Documentation updated
- [ ] Code review completed
- [ ] Story marked complete in index.md

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Accidentally remove needed code | High | Incremental removal with tests after each step |
| Break existing functionality | High | Comprehensive regression testing |
| Miss hidden dependencies | Medium | Thorough grep search before removal |
| User-facing API changes | Medium | Document breaking changes, provide migration guide |

---

**Document Version**: 1.0
**Created**: 2025-11-08 23:50
**Author**: Claude Agent SDK Team
