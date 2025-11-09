# Story 7: Update Tests for Color Changes

**Status**: unassigned
**Estimated Time**: 1 hour

---

## Dependencies

- Story 2 (unassigned) - Theme updates
- Story 3 (unassigned) - Tool formatting
- Story 4 (unassigned) - Syntax highlighting
- Story 5 (unassigned) - System messages
- Story 6 (unassigned) - Bullet indentation
- Story 9 (unassigned) - Pattern detection
- Story 10 (unassigned) - Structured data

---

## Description

Update existing theme and formatter tests to reflect new ANSI color mappings, component-level styling, and new features.

---

## Acceptance Criteria

- [ ] Update `tests/test_rendering_theme.py` for theme changes
- [ ] Update `tests/test_rendering_formatters.py` for component styling
- [ ] Add tests for syntax highlighting (Story 4)
- [ ] Add tests for system message visibility (Story 5)
- [ ] Add tests for bullet indentation (Story 6)
- [ ] Add tests for pattern detection (Story 9)
- [ ] Add tests for structured data (Story 10)
- [ ] All 556+ existing tests continue to pass
- [ ] Zero regressions from Sprint 1.3

---

## Technical Notes

- Focus files:
  - `tests/test_rendering_theme.py` (21 tests)
  - `tests/test_rendering_formatters.py`
  - `tests/test_rendering_formatters_color.py` (8 tests)
- Update golden outputs / snapshots if needed
- Verify ANSI escape sequences match expected

---

**Version**: 1.0 | **Created**: 2025-11-08
