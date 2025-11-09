# Story 5: Control System Message Visibility

**Status**: unassigned
**Estimated Time**: 1 hour

---

## Dependencies

- Story 2 (unassigned) - Theme foundation

---

## Description

Add render level control to hide "System: info" and "System: warning" messages by default, showing only critical system errors unless user requests detailed output.

---

## Acceptance Criteria

- [ ] Define system message severity levels: debug, info, warning, error, critical
- [ ] Update `RenderLevel` enum or add `SystemMessageLevel` config
- [ ] Default: Hide info/warning, show error/critical
- [ ] `RenderLevel.DETAILED` shows all system messages
- [ ] `RenderLevel.MINIMAL` shows only critical
- [ ] `RenderLevel.STANDARD` shows error and above (default)
- [ ] Update `format_system_message()` to respect visibility rules
- [ ] Tests for each render level + severity combination

---

## Technical Notes

- Location: `src/claude_agent_sdk/rendering/formatters.py:180-194`
- Parse message content to infer severity if type not available
- "System: info" → info level (hide by default)
- "System: warning" → warning level (hide by default)
- Cost displays → metadata (always show, styled dim)

---

**Version**: 1.0 | **Created**: 2025-11-08
