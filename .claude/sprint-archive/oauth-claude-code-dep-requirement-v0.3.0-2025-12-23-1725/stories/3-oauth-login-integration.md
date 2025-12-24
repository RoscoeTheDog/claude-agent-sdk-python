# Story 3: OAuth Login Integration

**Status**: unassigned
**Created**: 2025-12-21 21:37

## Description

Integrate CLI detection with existing oauth_login.py. The existing `trigger_oauth_login()` function uses hardcoded 'claude' command - it needs to use the new detection system.

## Acceptance Criteria

- [ ] (P0) `trigger_oauth_login()` uses `find_claude_cli()` instead of hardcoded 'claude'
- [ ] (P0) Catches `ClaudeCodeNotFoundError` and displays helpful message
- [ ] (P1) Returns False when CLI not found (graceful failure)
- [ ] (P0) Existing OAuth flow continues working when CLI is found

## Dependencies

- Story 1: CLI Detection Core
- Story 2: ClaudeCodeNotFoundError

## Implementation Notes

*To be added during implementation*

## Related Stories

- Story 1: CLI Detection Core (provides find_claude_cli)
- Story 2: ClaudeCodeNotFoundError (provides error class)
- Story 4: Optional Auto-OAuth Extra (extends with auto-install)
