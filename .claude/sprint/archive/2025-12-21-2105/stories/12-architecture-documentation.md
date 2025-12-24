# Story 12: Architecture & API Documentation

**Status**: unassigned
**Assignee**: unassigned
**Estimated Time**: 1.5 hours
**Actual Time**: TBD
**Priority**: HIGH
**Dependencies**: ALL other stories (2-11) must be completed first

---

## Description

Create comprehensive architecture documentation and API reference AFTER all implementation stories are complete. This ensures documentation accurately reflects the final implemented code, including any refactoring or changes made during development.

**Critical Principle**: Documentation is created as the **LAST STEP** of each story's implementation, not during or before. This prevents documentation drift when code is refactored.

**Goal**: Provide complete, accurate documentation for the syntax highlighting system that helps future developers understand and extend the architecture.

---

## Acceptance Criteria

### Per-Story Documentation (Created as LAST step of each story)

Each implementing agent must create documentation as their **final task** before marking story complete:

#### Story 2: Update Theme
- [ ] Document `semantic_mapping` field in `Theme` class
- [ ] Update `claude_code_default()` docstring
- [ ] Add usage examples for custom semantic mappings

#### Story 3: Tool Formatting
- [ ] Document state-based bullet coloring logic
- [ ] Document warning indicator thresholds
- [ ] Add examples of tool call formatting

#### Story 4: Unified Syntax Highlighting
- [ ] Document all 5 modules (language_registry, token_mapper, semantic_mapping, structured_formatter, highlighter)
- [ ] Create module-level docstrings with architecture overview
- [ ] Add class-level docstrings with usage examples
- [ ] Add method-level docstrings with Args/Returns/Examples
- [ ] Document the pipeline: detection → tokenization → semantic mapping → styling

#### Story 5: System Message Visibility
- [ ] Document render level controls
- [ ] Add examples of visibility filtering

#### Story 6: Bullet Indentation
- [ ] Document indentation algorithm
- [ ] Add examples of nested list rendering

#### Story 7: Update Tests
- [ ] Document test organization
- [ ] Add testing guide for syntax highlighting

#### Story 8: Update Docs
- [ ] Update user-facing documentation
- [ ] Add migration guide if APIs changed

#### Story 9: Pattern Detection
- [ ] Document pattern detection architecture
- [ ] Add examples of custom pattern registration

#### Story 11: Legacy Code Removal
- [ ] Document removed components (for migration guide)
- [ ] Document breaking changes (if any)

### Final Architecture Documentation (This Story - After ALL implementation complete)

Create comprehensive architecture docs in `.claude/implementation/architecture/`:

- [ ] `syntax-highlighting-architecture.md` - Complete system overview
- [ ] `api-reference.md` - Public API documentation
- [ ] `extension-guide.md` - How to add languages, customize mappings
- [ ] `migration-guide.md` - Upgrading from old architecture (if applicable)

### Documentation Verification (Final Check)

- [ ] Run full implementation and compare with documentation
- [ ] Verify all code examples in docs actually work
- [ ] Check for documentation drift (refactored code but old docs)
- [ ] Ensure docstrings match actual signatures
- [ ] Validate all cross-references are correct

---

## Documentation Standards

### Module Docstrings

Every `.py` file must have:

```python
"""Brief one-line description.

Extended description explaining the module's purpose, its role in
the architecture, and when/how to use it.

Architecture:
    - Explain where this fits in the overall system
    - List key dependencies
    - Note any important design decisions

Usage:
    >>> from module import Class
    >>> obj = Class(arg)
    >>> result = obj.method()
    >>> print(result)
    'expected output'

See Also:
    - Related modules
    - Architecture docs
"""
```

### Class Docstrings

Every class must have:

```python
class ExampleClass:
    """Brief one-line description.

    Extended description of what this class does, its responsibilities,
    and its role in the architecture.

    This class is responsible for X. It coordinates with Y module
    to achieve Z. Key design decisions include...

    Attributes:
        attr1: Description of attribute1
        attr2: Description of attribute2

    Example:
        >>> obj = ExampleClass(config)
        >>> result = obj.process(data)
        >>> print(result)
        'expected output'

    See Also:
        RelatedClass: Description of relationship
    """
```

### Method Docstrings

Every public method must have:

```python
def example_method(self, arg1: str, arg2: int = 0) -> str:
    """Brief one-line description.

    Extended description of what this method does, including
    any important implementation details or edge cases.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2 (default: 0)

    Returns:
        Description of return value

    Raises:
        ValueError: When arg1 is empty
        TypeError: When arg2 is negative

    Example:
        >>> obj = ExampleClass()
        >>> result = obj.example_method("test", 42)
        >>> print(result)
        'expected output'

    Note:
        Any important notes, warnings, or caveats
    """
```

---

## Architecture Documentation Structure

### File: `syntax-highlighting-architecture.md`

**Contents**:

1. **Overview**
   - What is the syntax highlighting system?
   - Why modular architecture?
   - Key design principles

2. **Architecture Diagram**
   ```
   Code Input
      ↓
   LanguageRegistry.detect(hint) → LanguageSpec
      ↓
   [Branch 1: Data Formats]        [Branch 2: General Languages]
   StructuredDataFormatter         Pygments Lexer
      ↓                               ↓
   Type-based coloring            TokenMapper.map_token()
      ↓                               ↓
   SemanticMapping                SemanticMapping
      ↓                               ↓
   Theme.get_style()              Theme.get_style()
      ↓                               ↓
   ANSIEncoder.encode()           ANSIEncoder.encode()
      ↓                               ↓
   Styled Output ←─────────────────┘
   ```

3. **Module Responsibilities**
   - LanguageRegistry: Language catalog and detection
   - TokenMapper: Pygments token → semantic category
   - SemanticMapping: Semantic category → theme color
   - StructuredDataFormatter: Type-aware JSON/YAML
   - SyntaxHighlighter: Orchestration

4. **Data Flow**
   - Step-by-step explanation of highlighting pipeline
   - Example traces for Python, JSON, unknown language

5. **Design Decisions**
   - Why separate semantic mapping from theme?
   - Why use semantic formatter for JSON/YAML vs Pygments?
   - Why token hierarchy fallback?

6. **Extension Points**
   - Adding new languages
   - Customizing semantic mappings
   - Adding new semantic formatters

---

### File: `api-reference.md`

**Contents**:

1. **Public Classes**
   - `SyntaxHighlighter`
   - `LanguageRegistry`
   - `SemanticMapping`
   - `StructuredDataFormatter`

2. **Public Methods**
   - Full signature + description for each

3. **Configuration**
   - `RendererConfig.enable_syntax_highlighting`
   - `Theme.semantic_mapping`

4. **Code Examples**
   ```python
   # Basic usage
   from claude_agent_sdk.rendering import RendererConfig, Theme
   from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

   theme = Theme.claude_code_default()
   highlighter = SyntaxHighlighter(theme)
   highlighted = highlighter.highlight(code, language_hint="python")
   ```

---

### File: `extension-guide.md`

**Contents**:

1. **Adding a New Language**
   ```python
   # In language_registry.py
   "elixir": LanguageSpec(
       name="Elixir",
       aliases=["elixir", "ex"],
       pygments_lexer="elixir",
       category="general_purpose"
   )
   ```

2. **Customizing Syntax Colors**
   ```python
   # Make comments dim instead of green
   custom_mapping = SemanticMapping.claude_default().customize({
       "comment": "metadata"
   })
   theme.semantic_mapping = custom_mapping
   ```

3. **Adding a Custom Semantic Formatter**
   ```python
   # For specialized data format
   class TOMLFormatter:
       def format_toml(self, data: str) -> str:
           # Custom TOML formatting logic
           pass
   ```

4. **Adding New Semantic Categories**
   ```python
   # In token_mapper.py, add new category
   Token.Name.Annotation: "annotation"  # New category

   # In semantic_mapping.py, map to theme color
   "annotation": "info"  # cyan
   ```

---

### File: `migration-guide.md`

**Contents** (if applicable):

1. **Breaking Changes**
   - Old API vs New API
   - Deprecated functions/classes

2. **Migration Examples**
   ```python
   # Old (if existed)
   highlighter = CodeHighlighter()
   result = highlighter.highlight_python(code)

   # New
   from claude_agent_sdk.rendering.syntax import SyntaxHighlighter
   highlighter = SyntaxHighlighter(theme)
   result = highlighter.highlight(code, language_hint="python")
   ```

3. **Compatibility Notes**
   - What still works?
   - What requires changes?

---

## Documentation Verification Checklist

**CRITICAL**: This checklist MUST be completed as the FINAL step before marking this story done.

### Code Example Verification
- [ ] Extract all code examples from documentation
- [ ] Create test file: `tests/test_documentation_examples.py`
- [ ] Run each example in actual code
- [ ] Verify outputs match documentation
- [ ] Fix any discrepancies

### Cross-Reference Verification
- [ ] Check all internal links work (module → module references)
- [ ] Verify all "See Also" references are valid
- [ ] Ensure all mentioned files/classes/methods exist
- [ ] Fix any broken references

### Signature Verification
- [ ] Compare documented method signatures with actual code
- [ ] Check parameter types match
- [ ] Verify return types match
- [ ] Ensure default values are accurate

### Drift Detection
For each story (2-11):
- [ ] Re-read the implementation
- [ ] Compare with documentation created during that story
- [ ] Check if any refactoring occurred after docs written
- [ ] Update docs if drift detected

### Architecture Diagram Verification
- [ ] Walk through code following the architecture diagram
- [ ] Verify each arrow/step actually exists in code
- [ ] Check for missing steps or modules
- [ ] Update diagram if discrepancies found

---

## Implementation Process

### Phase 1: Collect Per-Story Docs (30 min)

Review each completed story's documentation:

```bash
# Check Story 2 docs
grep -A 50 "semantic_mapping" src/claude_agent_sdk/rendering/theme.py

# Check Story 4 docs
ls src/claude_agent_sdk/rendering/syntax/
cat src/claude_agent_sdk/rendering/syntax/*.py | grep -A 20 '"""'

# ... repeat for each story
```

### Phase 2: Create Architecture Docs (45 min)

Create the 4 architecture docs listed above:

```bash
mkdir -p .claude/implementation/architecture

# Create each doc
touch .claude/implementation/architecture/syntax-highlighting-architecture.md
touch .claude/implementation/architecture/api-reference.md
touch .claude/implementation/architecture/extension-guide.md
touch .claude/implementation/architecture/migration-guide.md

# Populate with content
```

### Phase 3: Verification (15 min)

Run the verification checklist above.

Create automated verification test:

```python
# tests/test_documentation_examples.py
"""Verify all documentation code examples work."""

def test_basic_usage_example():
    """Test example from api-reference.md."""
    from claude_agent_sdk.rendering import RendererConfig, Theme
    from claude_agent_sdk.rendering.syntax import SyntaxHighlighter

    theme = Theme.claude_code_default()
    highlighter = SyntaxHighlighter(theme)

    code = "def hello(): pass"
    highlighted = highlighter.highlight(code, language_hint="python")

    assert "def" in highlighted
    assert highlighted != code  # Should have ANSI codes

def test_language_addition_example():
    """Test example from extension-guide.md."""
    from claude_agent_sdk.rendering.syntax import LanguageRegistry

    # Verify example language exists
    lang = LanguageRegistry.get_by_id("python")
    assert lang is not None
    assert lang.pygments_lexer == "python"

def test_customization_example():
    """Test example from extension-guide.md."""
    from claude_agent_sdk.rendering.syntax import SemanticMapping

    # Custom mapping example
    custom = SemanticMapping.claude_default().customize({
        "comment": "metadata"
    })

    assert custom.get_theme_category("comment") == "metadata"

# Add test for every code example in documentation
```

Run tests:

```bash
python -m pytest tests/test_documentation_examples.py -v
```

If tests fail, update documentation to match reality.

---

## Completion Checklist

- [ ] Verified all stories (2-11) have inline documentation
- [ ] Created `syntax-highlighting-architecture.md`
- [ ] Created `api-reference.md`
- [ ] Created `extension-guide.md`
- [ ] Created `migration-guide.md` (if needed)
- [ ] Ran documentation verification checklist
- [ ] Created `test_documentation_examples.py`
- [ ] All documentation example tests passing
- [ ] Fixed any documentation drift from refactoring
- [ ] Updated cross-references
- [ ] Verified signatures match code
- [ ] Code review of documentation
- [ ] Story marked complete in index.md

---

## Why Documentation Comes Last

**Problem**: Documentation written during implementation often becomes outdated due to refactoring.

**Example**:
1. Agent implements `TokenMapper` with method `map_token(token)`
2. Agent documents it: "Call `map_token(token)` to map tokens"
3. During testing, agent refactors to `map_token(token, fallback=True)`
4. Documentation now incorrect!

**Solution**: Document AFTER implementation complete:
1. Agent completes all implementation and testing
2. Agent refactors as needed
3. Agent documents final implementation (no more changes)
4. Documentation matches reality

**Final Verification**: Story 12 re-checks ALL documentation against actual code to catch any missed updates.

---

**Document Version**: 1.0
**Created**: 2025-11-08 23:55
**Author**: Claude Agent SDK Team
