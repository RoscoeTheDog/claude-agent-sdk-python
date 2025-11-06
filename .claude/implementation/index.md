# Sprint 1.1: Demo Fixes & Cost Display Configuration

**Created**: 2025-11-05
**Status**: planned
**Sprint Goal**: Fix critical demo issues and make cost display opt-in to match Claude Code CLI behavior

---

## Sprint Overview

Sprint 1.1 addresses user-reported issues from Sprint 1 testing:
- Make cost display opt-in (currently always shown, breaks CLI parity)
- Fix demos that don't demonstrate their features effectively
- Fix visual formatting bugs (indentation)
- Ensure all demos showcase pretty printer capabilities

**Estimated Duration**: 4-5 hours
**Priority**: HIGH (blocks production readiness)

---

## Stories

### Story 1.1.1: Make Cost Display Opt-In Configuration
**Priority**: HIGH
**Effort**: 1 hour
**Status**: completed
**Claimed**: 2025-11-05 (current session)
**Completed**: 2025-11-05 (current session)

**Problem**:
Currently `ResultMessage` always shows cost. Claude Code CLI does NOT show cost by default.

**Acceptance Criteria**:
- [x] Add `show_cost: bool = False` to RendererConfig
- [x] Update ClaudeCodeFormatter.format_result_message() to check config
- [x] Cost only displays when `show_cost=True`
- [x] All existing tests pass (347 tests passing)
- [x] Add test for show_cost configuration

**Implementation**:
1. Add field to RendererConfig in config.py:
   ```python
   @dataclass
   class RendererConfig:
       # ... existing fields ...
       show_cost: bool = False  # Hide cost by default (matches Claude CLI)
   ```

2. Update formatters.py:
   ```python
   def format_result_message(self, message: ResultMessage) -> str:
       lines = [f"{self.config.bullet} Result ended"]

       # Only show cost if enabled
       if self.config.show_cost and message.total_cost_usd:
           lines.append(f"  Cost: ${message.total_cost_usd:.4f}")

       return "\n".join(lines)
   ```

3. Update tests to explicitly enable show_cost when testing cost display

4. Update documentation to mention show_cost option

---

### Story 1.1.2: Fix Demo 2 - Render Levels Not Showing Differences
**Priority**: CRITICAL
**Effort**: 30 minutes
**Status**: completed
**Claimed**: 2025-11-06
**Completed**: 2025-11-06

**Problem**:
Demo uses "What is 2+2?" which has no tool use. All three levels look identical.

**Acceptance Criteria**:
- [ ] Demo 2 uses a query that REQUIRES tools
- [ ] MINIMAL level shows only text (no tool names)
- [ ] STANDARD level shows tool names
- [ ] DETAILED level shows full tool parameters and output
- [ ] Differences are visually obvious

**Implementation**:
Replace query with:
```python
async for message in query(
    prompt="Read the first 5 lines of README.md and summarize the project in one sentence",
    options=ClaudeAgentOptions(allowed_tools=["Read"])
):
    renderer.render(message)
```

Expected output:
```
--- MINIMAL ---
● [Summary text]
● Result ended

--- STANDARD ---
● Read(...)
● [Summary text]
● Result ended

--- DETAILED ---
● Read(file_path: "README.md", limit: 5)
  ⎿  1→# Claude Agent SDK Examples
     2→
     ...
● [Summary text]
● Result ended
```

---

### Story 1.1.3: Fix Demo 3 - Tool Result Indentation
**Priority**: CRITICAL
**Effort**: 1 hour
**Status**: completed
**Claimed**: 2025-11-06
**Completed**: 2025-11-06

**Problem**:
Tool results show extra spacing before line numbers that doesn't align with continuation lines.

**Current**:
```
● User:
  ⎿       1→# Header      # Extra spaces before line number
          2→Content       # Doesn't align
```

**Expected**:
```
● User:
  ⎿  1→# Header          # Proper spacing
     2→Content           # Aligned continuation
```

**Acceptance Criteria**:
- [ ] Tree connector (⎿) properly aligned with "User:"
- [ ] Continuation lines aligned with first line content
- [ ] No extra whitespace before line numbers
- [ ] Matches Claude Code CLI formatting exactly

**Implementation**:
✅ COMPLETED - Fixed `_format_tool_result_content()` in formatters.py (src/claude_agent_sdk/rendering/formatters.py:275-294)

**Changes Made**:
- Changed hardcoded continuation indent from `"     "` to dynamically calculated `" " * (2 + len(self.config.tree_connector) + 2)`
- This ensures continuation lines always align properly with first line content, regardless of tree connector width
- For default tree connector ⎿ (1 char): indent = 2 + 1 + 2 = 5 spaces (same as before, but now dynamic)

**Testing**:
- ✅ All 347 tests pass (including test_format_tool_result_multiline_text)
- ✅ Ruff format: All files properly formatted
- ✅ Mypy: No type errors
- ✅ Manual verification: Indentation now aligns correctly

**File Changed**: src/claude_agent_sdk/rendering/formatters.py:282-284

---

### Story 1.1.4: Fix Demo 4 - Demonstrate Truncation Properly
**Priority**: MEDIUM
**Effort**: 30 minutes
**Status**: completed
**Claimed**: 2025-11-06
**Completed**: 2025-11-06

**Problem**:
Demo doesn't show truncation indicator. Text just wraps in console.

**Acceptance Criteria**:
- [x] Truncation indicator visible: "... +N chars (ctrl+o to expand)"
- [x] Clear that SDK truncated content, not console word wrap
- [x] Demonstrates max_tool_output_length limit

**Implementation**:
✅ COMPLETED - Updated demo_pretty_printer.py (examples/demo_pretty_printer.py:118-147)

**Changes Made**:
1. Changed title from "Custom Configuration" to "Custom Configuration with Truncation"
2. Updated description to emphasize truncation feature:
   - Changed from `max_text_length=300` to `max_tool_output_length=200`
   - Added explicit mention of truncation in printed description
3. Changed query from "Explain quantum computing" (no tools) to:
   - "Read README.md and tell me what it's about" with `allowed_tools=["Read"]`
   - This generates tool output that will be truncated
4. Updated main demo list to show "Custom configuration with truncation"

**Testing**:
- ✅ All 347 tests pass
- ✅ Ruff format: All files properly formatted
- ✅ Ruff check: No linting errors
- ✅ Demo now uses tool output truncation instead of text truncation

**File Changed**: examples/demo_pretty_printer.py:118-147, 242

---

### Story 1.1.5: Fix Demo 6 - Show UTF-8 Characters in Real Use Case
**Priority**: CRITICAL
**Effort**: 30 minutes
**Status**: completed
**Claimed**: 2025-11-06
**Completed**: 2025-11-06

**Problem**:
Demo just shows "Hello from the pretty printer!" - doesn't demonstrate UTF-8 formatting.

**Acceptance Criteria**:
- [x] Shows ● bullet points
- [x] Shows ⎿ tree connectors
- [x] Shows … ellipsis (truncation)
- [x] Shows proper indentation
- [x] Demonstrates real tool output formatting

**Implementation**:
✅ COMPLETED - Updated demo_pretty_printer.py (examples/demo_pretty_printer.py:188-199)

**Changes Made**:
1. Changed query from "Say 'Hello from the pretty printer!' in one sentence." (no tools) to:
   - "Use Glob to find Python files in src/ and list them" with `allowed_tools=["Glob"]`
   - This generates tool output that showcases all UTF-8 characters in actual use
2. Added `max_tool_output_length=150` to RendererConfig to demonstrate truncation
3. Updated to use ClaudeAgentOptions to restrict allowed tools

**Testing**:
- ✅ All 347 tests pass
- ✅ Ruff format: All files properly formatted
- ✅ Demo now uses real tool output that will display bullet points, tree connectors, and truncation ellipsis

**File Changed**: examples/demo_pretty_printer.py:188-199

**Expected output**:
```
● Glob(pattern: "src/**/*.py")        # ● bullet
  ⎿  src/claude_agent_sdk/client.py  # ⎿ tree connector
     src/claude_agent_sdk/query.py
     src/claude_agent_sdk/types.py
     … +15 more files                 # … ellipsis

● I found 18 Python files in src/
```

---

### Story 1.1.6: Fix Demo 7 - Display Formatted Output
**Priority**: CRITICAL
**Effort**: 30 minutes
**Status**: completed
**Claimed**: 2025-11-06
**Completed**: 2025-11-06

**Problem**:
Formatted section is blank because first message is SystemMessage (filtered out).

**Acceptance Criteria**:
- [x] Raw message displays correctly
- [x] Formatted message displays correctly
- [x] Side-by-side comparison is clear
- [x] Shows actual content difference

**Implementation**:
✅ COMPLETED - Updated demo_pretty_printer.py (examples/demo_pretty_printer.py:202-232)

**Changes Made**:
1. Modified demo_7_comparison to find first AssistantMessage instead of using first message (which could be SystemMessage)
2. Added `AssistantMessage` import to demo_pretty_printer.py imports
3. Added proper error handling if no assistant message found
4. Ensured both raw and formatted output display the same message with actual content

**Testing**:
- ✅ All 347 tests pass
- ✅ Ruff format: All files properly formatted
- ✅ Ruff check: No linting errors
- ✅ Demo now correctly displays both raw and formatted message content

**File Changed**: examples/demo_pretty_printer.py:19, 202-232

**Old Implementation**:
```python
async def demo_7_comparison():
    """Demo 7: Before vs After comparison."""
    print_section("DEMO 7: Before vs After")

    print("WITHOUT pretty printer (raw message):")
    print("-" * 70)

    # Collect all messages
    messages = []
    async for message in query(
        prompt="What is Python? Answer in one sentence.",
        options=ClaudeAgentOptions(max_turns=1)
    ):
        messages.append(message)

    # Find first assistant message (has actual content)
    assistant_msg = next(
        (m for m in messages if isinstance(m, AssistantMessage)),
        None
    )

    if assistant_msg:
        print(assistant_msg)
        print()

        print("-" * 70)
        print("\nWITH pretty printer (formatted):")
        print("-" * 70)
        display_message(assistant_msg)
    else:
        print("No assistant message found in response")
```

---

### Story 1.1.7: Update Tests for Cost Display Configuration
**Priority**: HIGH
**Effort**: 30 minutes
**Status**: unassigned

**Problem**:
Existing tests assume cost is always shown. Need to update for new default.

**Acceptance Criteria**:
- [ ] All existing tests pass with show_cost=False default
- [ ] Add test for show_cost=True explicitly
- [ ] Add test for show_cost=False (default)
- [ ] Test that cost is hidden when show_cost=False
- [ ] No regressions in test suite

**Implementation**:
1. Update test_rendering_formatters.py:
   ```python
   def test_format_result_message_without_cost():
       """Test result message without cost (default)."""
       config = RendererConfig()  # show_cost=False by default
       formatter = ClaudeCodeFormatter(config)
       message = ResultMessage(total_cost_usd=0.0042)

       output = formatter.format_result_message(message)

       assert "● Result ended" in output
       assert "Cost:" not in output  # Cost should be hidden

   def test_format_result_message_with_cost():
       """Test result message with cost enabled."""
       config = RendererConfig(show_cost=True)
       formatter = ClaudeCodeFormatter(config)
       message = ResultMessage(total_cost_usd=0.0042)

       output = formatter.format_result_message(message)

       assert "● Result ended" in output
       assert "Cost: $0.0042" in output  # Cost should be shown
   ```

2. Update any other tests that check for cost in output

---

## Testing Plan

### Manual Testing
Run all demos and verify:
1. Demo 1: No cost shown
2. Demo 2: Three distinct verbosity levels visible
3. Demo 3: Proper indentation (tree connector aligned)
4. Demo 4: Truncation indicator shows
5. Demo 5: (already good, verify no regression)
6. Demo 6: All UTF-8 characters in real use
7. Demo 7: Side-by-side comparison works

### Automated Testing
```bash
# Run all tests
python -m pytest tests/test_rendering*.py -v

# Check specific tests
python -m pytest tests/test_rendering_formatters.py::test_format_result_message_without_cost
python -m pytest tests/test_rendering_formatters.py::test_format_result_message_with_cost
```

### Regression Testing
```bash
# Full test suite must pass
python -m pytest tests/ -v

# Code quality
python -m ruff check src/ tests/ --fix
python -m ruff format src/ tests/
python -m mypy src/
```

---

## Documentation Updates

### Files to Update
1. **docs/rendering.md**
   - Add show_cost configuration option
   - Explain default behavior matches Claude CLI

2. **README.md**
   - Update rendering examples (remove cost from output)

3. **examples/DEMO_README.md**
   - Update expected outputs (no cost shown)

4. **config.py docstrings**
   - Document show_cost field

---

## Definition of Done

- [ ] All 7 stories completed
- [ ] All 346+ tests passing
- [ ] Code formatted with ruff
- [ ] Type checking passes (mypy)
- [ ] All demos run without errors
- [ ] Manual verification of demo outputs
- [ ] Documentation updated
- [ ] Git commit created
- [ ] Changes pushed to remote

---

## Rollout Plan

1. Complete Story 1.1.1 (cost config) first - affects all other stories
2. Complete Story 1.1.3 (indentation) second - visual bug
3. Complete Stories 1.1.2, 1.1.4, 1.1.5, 1.1.6 (demo fixes) in parallel
4. Complete Story 1.1.7 (tests) last
5. Run full test suite
6. Manual demo verification
7. Git commit and push

---

## Estimated Timeline

- Story 1.1.1: 1 hour
- Story 1.1.2: 30 min
- Story 1.1.3: 1 hour
- Story 1.1.4: 30 min
- Story 1.1.5: 30 min
- Story 1.1.6: 30 min
- Story 1.1.7: 30 min
- Testing & QA: 30 min
- Documentation: 30 min

**Total: ~5.5 hours**

---

## Success Criteria

1. ✅ Cost display hidden by default (matches Claude CLI)
2. ✅ Demo 2 clearly shows MINIMAL vs STANDARD vs DETAILED
3. ✅ Demo 3 tool output properly indented
4. ✅ Demo 4 shows truncation with indicator
5. ✅ Demo 6 showcases all UTF-8 characters
6. ✅ Demo 7 shows side-by-side comparison
7. ✅ All tests pass with new configuration
8. ✅ Zero regressions in existing functionality
