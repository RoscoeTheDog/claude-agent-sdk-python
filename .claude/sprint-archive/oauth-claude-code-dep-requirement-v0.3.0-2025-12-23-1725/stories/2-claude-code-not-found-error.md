# Story 2: ClaudeCodeNotFoundError

**Status**: unassigned
**Created**: 2025-12-21 21:37

## Description

Create helpful error class with installation instructions. When Claude Code CLI is not found, users need clear guidance on how to install it.

## Acceptance Criteria

- [ ] (P0) `ClaudeCodeNotFoundError` exception class defined
- [ ] (P0) Error message includes npm install command
- [ ] (P1) Error message includes Homebrew install for macOS
- [ ] (P1) Error message includes auto-oauth pip extra option
- [ ] (P2) Error message includes link to Anthropic docs

## Dependencies

None

## Implementation Notes

*To be added during implementation*

## Related Stories

- Story 1: CLI Detection Core (raises this error)
- Story 3: OAuth Login Integration (catches this error)
