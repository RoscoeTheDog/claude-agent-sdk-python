# Story 5: Cross-Platform Testing

**Status**: unassigned
**Created**: 2025-12-21 21:37

## Description

Test CLI detection across Windows, macOS, and Linux paths. Comprehensive unit tests ensure the detection logic works correctly on all platforms.

## Acceptance Criteria

- [ ] (P0) Unit tests verify PATH detection via mocked shutil.which
- [ ] (P0) Unit tests verify local install path (~/.claude/bin/) detection
- [ ] (P1) Unit tests verify platform-specific paths per OS
- [ ] (P1) Unit tests verify ClaudeCodeNotFoundError message content
- [ ] (P2) Integration test with actual CLI if available in CI

## Dependencies

- Story 1: CLI Detection Core
- Story 2: ClaudeCodeNotFoundError
- Story 3: OAuth Login Integration

## Implementation Notes

*To be added during implementation*

## Related Stories

- Story 1: CLI Detection Core (tests this)
- Story 2: ClaudeCodeNotFoundError (tests this)
- Story 3: OAuth Login Integration (tests this)
