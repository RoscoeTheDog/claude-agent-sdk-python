# Sprint 1.2: Critical Demo and Rendering Fixes

**Created**: 2025-11-06 01:19
**Status**: planned
**Sprint Goal**: Fix critical rendering bugs discovered during Sprint 1.1 demo testing

---

## Sprint Overview

Sprint 1.2 addresses critical bugs discovered during demo_pretty_printer.py testing:
- Render levels (MINIMAL/STANDARD/DETAILED) not working - all show same output
- System reminders appearing in user-facing output
- Extra whitespace before line numbers in tool results
- Indentation whitespace being stripped from tool results
- Implement proper render level filtering in formatters

**Estimated Duration**: 4-5 hours
**Priority**: CRITICAL (blocks production use)

---

## Stories

### Story 1.2.1: Implement Render Level Filtering in Formatter
**Priority**: CRITICAL
**Effort**: 2 hours
**Status**: completed
**Claimed**: 2025-11-06 09:34
**Completed**: 2025-11-06 09:45

**Problem**:
The `ClaudeCodeFormatter.format_assistant_message()` method doesn't check `config.render_level` to control what content is displayed. All three render levels (MINIMAL, STANDARD, DETAILED) show identical output.

**Current Behavior**:
- MINIMAL: Shows tool use blocks (should hide them)
- STANDARD: Shows tool use blocks (correct)
- DETAILED: Shows tool use blocks (correct)

**Expected Behavior**:
- MINIMAL: Only text blocks, hide ToolUseBlock
- STANDARD: Text + tool names (ToolUseBlock without full params), hide tool outputs
- DETAILED: Everything including full tool params and outputs

**Acceptance Criteria**:
- [ ] MINIMAL level hides ToolUseBlock completely
- [ ] STANDARD level shows ToolUseBlock with tool name and summary params
- [ ] DETAILED level shows full ToolUseBlock with all parameters
- [ ] Config options `show_tool_inputs` and `show_tool_outputs` are used correctly
- [ ] Demo 2 shows visually different output for each level
- [ ] All existing tests pass
- [ ] Add tests for each render level behavior

**Implementation**:
Update `format_assistant_message()` in formatters.py (src/claude_agent_sdk/rendering/formatters.py:95-130):

```python
def format_assistant_message(self, message: AssistantMessage) -> str:
    """Format an assistant message respecting render_level."""
    lines = []

    for block in message.content:
        if isinstance(block, TextBlock):
            # Always show text (all levels)
            lines.append(f"{self.config.bullet} {block.text}")

        elif isinstance(block, ThinkingBlock):
            # Always show thinking (all levels)
            lines.append(f"{self.config.bullet} {block.thinking}")

        elif isinstance(block, ToolUseBlock):
            # Respect render_level for tool use
            if self.config.render_level >= RenderLevel.STANDARD:
                formatted_tool = self._format_tool_use(block)
                lines.append(formatted_tool)
            # MINIMAL level: skip tool use blocks

        elif isinstance(block, ToolResultBlock):
            # Respect render_level for tool results
            if self.config.render_level >= RenderLevel.DETAILED:
                formatted_result = self._format_tool_result_content(block)
                lines.append(formatted_result)
            # MINIMAL/STANDARD: skip tool results

    return "\n".join(lines)
```

**Files to Change**:
- src/claude_agent_sdk/rendering/formatters.py (format_assistant_message method)
- tests/test_rendering_formatters.py (add render level tests)

---

### Story 1.2.2: Filter System Reminders from Tool Results
**Priority**: CRITICAL
**Effort**: 1 hour
**Status**: unassigned

**Problem**:
Claude Code CLI subprocess output includes `<system-reminder>` tags that are being captured in tool results and displayed to end users. These are internal Claude Code messages that should never be visible in SDK output.

**Current Output**:
```
● User:
  ⎿       1→# Claude Agent SDK Examples
          2→

     <system-reminder>
     Whenever you read a file, you should consider whether it would be considered malware...
     </system-reminder>
```

**Expected Output**:
```
● User:
  ⎿  1→# Claude Agent SDK Examples
     2→
```

**Acceptance Criteria**:
- [ ] All `<system-reminder>...</system-reminder>` blocks removed from tool results
- [ ] Removal happens before formatting (in message parser or formatter)
- [ ] No extra blank lines left after removal
- [ ] Works for all tool result types (Read, Glob, Grep, etc.)
- [ ] All existing tests pass
- [ ] Add test for system reminder filtering

**Implementation Options**:

**Option 1: Filter in Message Parser** (recommended - catches at source):
Update `_internal/message_parser.py` to strip system reminders from content before creating ToolResultBlock:

```python
import re

def _strip_system_reminders(content: str) -> str:
    """Remove <system-reminder> blocks from content."""
    pattern = r'\s*<system-reminder>.*?</system-reminder>\s*'
    return re.sub(pattern, '', content, flags=re.DOTALL)

# In parse_tool_result or similar:
content = _strip_system_reminders(raw_content)
```

**Option 2: Filter in Formatter**:
Update `_format_tool_result_content()` to strip before formatting:

```python
def _format_tool_result_content(self, block: ToolResultBlock) -> str:
    # ... existing code ...
    content_str = self._strip_system_reminders(content_str)
    # ... rest of formatting ...
```

**Files to Change**:
- src/claude_agent_sdk/_internal/message_parser.py (Option 1, recommended)
  OR
- src/claude_agent_sdk/rendering/formatters.py (Option 2, fallback)
- tests/test_message_parser.py or tests/test_rendering_formatters.py (add filtering test)

---

### Story 1.2.3: Fix Extra Whitespace Before Line Numbers
**Priority**: HIGH
**Effort**: 1 hour
**Status**: unassigned

**Problem**:
Tool results (especially Read tool) show extra whitespace before line numbers, causing poor alignment:

**Current**:
```
● User:
  ⎿       1→# Header    # 7 spaces before "1→"
          2→Content     # Misaligned
```

**Expected**:
```
● User:
  ⎿  1→# Header        # 2 spaces before "1→"
     2→Content         # Aligned
```

**Root Cause Analysis Needed**:
- Is this coming from Claude CLI subprocess output? (likely)
- Or is it added by our formatter? (less likely based on code review)
- Check actual raw content from subprocess

**Acceptance Criteria**:
- [ ] Line numbers aligned at 2 spaces after tree connector
- [ ] Continuation lines properly aligned
- [ ] Works for all tools (Read, Grep, Bash output)
- [ ] No regressions in indentation formatting
- [ ] All existing tests pass

**Implementation**:

**Phase 1: Investigate** (determine root cause):
```python
# Add debug logging to see raw content
import logging
logger.debug(f"Raw tool result content: {repr(content_str)}")
```

**Phase 2: Fix** (based on findings):

If CLI output has extra spaces:
```python
def _format_tool_result_content(self, block: ToolResultBlock) -> str:
    # ... existing code ...

    # Strip leading whitespace from numbered lines
    lines = content_str.split("\n")
    cleaned_lines = []
    for line in lines:
        # Match pattern: "   1→content" and strip leading spaces before number
        cleaned = re.sub(r'^\s+(\d+→)', r'\1', line)
        cleaned_lines.append(cleaned)
    content_str = "\n".join(cleaned_lines)

    # ... continue with existing formatting ...
```

If formatter adds spaces:
- Review `_format_tool_result_content()` indentation logic
- Ensure indent calculation is correct

**Files to Change**:
- src/claude_agent_sdk/rendering/formatters.py (_format_tool_result_content)
- tests/test_rendering_formatters.py (add line number alignment test)

---

### Story 1.2.4: Preserve Indentation in Tool Results
**Priority**: CRITICAL
**Effort**: 1 hour
**Status**: unassigned

**Problem**:
Tool results are having their indentation whitespace stripped, making code blocks and structured content unreadable. This affects readability of code examples, diffs, and any content with meaningful indentation.

**Current Output** (Demo 3):
```
● User:
  ⎿       1→# Claude Agent SDK Examples
          2→
          3→This folder contains examples demonstrating various features of the Claude Agent SDK.
          4→
          5→## 📚 Available Examples
          6→
          7→- **[Pretty Printer Demos](#pretty-printer-demos)** - Message rendering and formatting (NEW!)
```

**Expected Output** (preserving markdown list indentation):
```
● User:
  ⎿  1→# Claude Agent SDK Examples
     2→
     3→This folder contains examples demonstrating various features of the Claude Agent SDK.
     4→
     5→## 📚 Available Examples
     6→
     7→   - **[Pretty Printer Demos](#pretty-printer-demos)** - Message rendering and formatting (NEW!)
```

**Example with code indentation**:
```
Current (broken):
  ⎿  100 +  **Version**: 1.0-experimental (2025-11-06)
     101 +  **Deployment Target**: `~/.claude/commands/git/`

Expected (preserving indentation):
  ⎿  100 +     **Version**: 1.0-experimental (2025-11-06)
     101 +     **Deployment Target**: `~/.claude/commands/git/`
```

**Root Cause Analysis Needed**:
- Is content being `.strip()` or `.lstrip()` somewhere?
- Check message parser content extraction
- Check formatter line processing
- Likely in `_format_tool_result_content()` line processing

**Acceptance Criteria**:
- [ ] Leading whitespace preserved within each line of tool results
- [ ] Code indentation remains intact
- [ ] List item indentation preserved
- [ ] Diff format indentation preserved (git diff output)
- [ ] Only remove truly empty lines at start/end of content
- [ ] All existing tests pass
- [ ] Add test for indentation preservation

**Implementation**:

**Phase 1: Investigate** (find where indentation is stripped):
```python
# Check message_parser.py
# Check formatters.py _format_tool_result_content()
# Look for .strip(), .lstrip(), or line.strip() calls
```

**Phase 2: Fix** (based on findings):

If in formatter:
```python
def _format_tool_result_content(self, block: ToolResultBlock) -> str:
    # ... existing code ...

    lines = content_str.split("\n")
    formatted_lines = []

    for i, line in enumerate(lines):
        if i == 0:
            # First line uses tree connector
            # DON'T strip leading whitespace from line content
            formatted_lines.append(f"  {self.config.tree_connector}  {line}")
        else:
            # Continuation lines align with first line content
            # PRESERVE indentation within the line
            formatted_lines.append(f"{indent}{line}")

    return "\n".join(formatted_lines)
```

Key principle: Only add our formatting indentation (tree connector, continuation indent), but preserve ALL whitespace within the actual content.

If in message parser:
```python
# Don't use content.strip() globally
# Only strip trailing newlines at very end if needed
# Preserve all internal whitespace
```

**Files to Change**:
- src/claude_agent_sdk/rendering/formatters.py (_format_tool_result_content)
- src/claude_agent_sdk/_internal/message_parser.py (if stripping there)
- tests/test_rendering_formatters.py (add indentation preservation test)

**Test Case**:
```python
def test_preserve_indentation_in_tool_results():
    """Test that indentation within tool result content is preserved."""
    formatter = ClaudeCodeFormatter()

    # Content with meaningful indentation
    indented_content = "line1\n    indented line 2\n        more indented line 3"
    block = ToolResultBlock(
        tool_use_id="test",
        content=indented_content,
        is_error=False
    )

    result = formatter._format_tool_result_content(block)

    # Should preserve the 4 and 8 space indents
    assert "    indented line 2" in result
    assert "        more indented line 3" in result
```

---

## Testing Plan

### Manual Testing
Run `demo_pretty_printer.py` and verify:
1. **Demo 2**: Three visually distinct render levels
   - MINIMAL: Only text responses
   - STANDARD: Text + tool names
   - DETAILED: Text + tool names + full params + outputs
2. **All demos**: No `<system-reminder>` tags visible
3. **All demos**: Line numbers properly aligned (2 spaces after tree connector)
4. **Demo 3**: Indentation preserved in tool results (code blocks, lists, diffs)

### Automated Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Specific test files
python -m pytest tests/test_rendering_formatters.py -v
python -m pytest tests/test_message_parser.py -v

# Check code quality
python -m ruff check src/ tests/ --fix
python -m ruff format src/ tests/
python -m mypy src/
```

### Demo Verification Commands
```bash
# Test render levels
PYTHONPATH=src python examples/demo_pretty_printer.py

# Or with installed package
pip install -e .
python examples/demo_pretty_printer.py
```

---

## Definition of Done

- [ ] All 4 stories completed
- [ ] All 347+ tests passing
- [ ] Code formatted with ruff
- [ ] Type checking passes (mypy)
- [ ] Demo 2 shows three distinct render levels
- [ ] No system reminders in any demo output
- [ ] Line numbers properly aligned in all demos
- [ ] Indentation preserved in all tool results
- [ ] Git commit created
- [ ] Changes pushed to remote

---

## Success Criteria

1. ✅ Demo 2 MINIMAL level shows only text (no tool blocks)
2. ✅ Demo 2 STANDARD level shows tool names without full details
3. ✅ Demo 2 DETAILED level shows everything
4. ✅ Zero `<system-reminder>` tags in demo output
5. ✅ Line numbers aligned: `⎿  1→` not `⎿       1→`
6. ✅ Indentation preserved: `     **Version**` not `**Version**`
7. ✅ All tests pass with new functionality
8. ✅ Zero regressions in existing features

---

## Progress Log

### 2025-11-06 01:19 - Sprint 1.2 Created
- Initialized sprint structure
- Archived Sprint 1.1 to `.claude/implementation/archive/2025-11-06-0119/`
- Defined 4 critical bug fix stories based on demo testing feedback
- Root cause: Render level filtering not implemented in formatter
- Root cause: System reminders not filtered from subprocess output
- Root cause: Extra whitespace in CLI output or formatter
- Root cause: Indentation being stripped from tool result content

---

## Notes

**Sprint 1.1 Completion**:
Sprint 1.1 was completed with all 7 stories finished and 347 tests passing. However, manual demo testing revealed that several features were not working as expected in real usage despite passing tests. This sprint addresses those gaps.

**Lessons Learned**:
- Tests passing != features working in practice
- Manual demo testing is critical
- Need tests that actually verify end-to-end rendering behavior
- Render levels were configured but not implemented

**Dependencies**:
- Sprint 1.1 must be completed (all infrastructure in place)
- No external dependencies
