# Story 6: Fix Bullet List Indentation

**Status**: unassigned
**Estimated Time**: 1.5 hours

---

## Dependencies

- Story 2 (unassigned) - Theme foundation

---

## Description

Fix indentation for nested bullet points and list items in assistant messages so subsequent lines and nested items align properly with the first bullet character position.

---

## Acceptance Criteria

- [ ] Top-level bullets (●) appear at left margin
- [ ] Nested list items (`-`, `*`, `1.`) indent from bullet position
- [ ] Multi-line list items wrap with hanging indent
- [ ] Tree connector (⎿) aligns consistently
- [ ] Preserve existing spacing for code blocks
- [ ] Update `format_assistant_message()` with proper indentation logic
- [ ] Tests for nested lists, multi-line items, mixed content

---

## Technical Notes

- Location: `src/claude_agent_sdk/rendering/formatters.py:126-178`
- Expected format:
  ```
  ● I've created a function with:
    - Input validation
    - Efficient algorithm
  ```
- May need markdown parser or custom list detection regex

---

**Version**: 1.0 | **Created**: 2025-11-08
