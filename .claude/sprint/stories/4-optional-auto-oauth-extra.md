# Story 4: Optional Auto-OAuth Extra

**Status**: unassigned
**Created**: 2025-12-21 21:37

## Description

Add nodejs-bin optional dependency for auto-install capability. This implements Approach E from the handoff spec as an optional fallback for users wanting zero-config OAuth support.

## Acceptance Criteria

- [ ] (P0) `pyproject.toml` defines `auto-oauth` optional dependency with nodejs-bin>=18.0.0
- [ ] (P0) `get_claude_cli_or_install()` function attempts auto-install when detection fails
- [ ] (P1) Auto-install uses npm to install @anthropic-ai/claude-code to ~/.claude-sdk/
- [ ] (P1) Falls back to `ClaudeCodeNotFoundError` if auto-install fails
- [ ] (P2) Gracefully handles ImportError when nodejs-bin not installed

## Dependencies

- Story 1: CLI Detection Core
- Story 2: ClaudeCodeNotFoundError

## Implementation Notes

*To be added during implementation*

## Related Stories

- Story 1: CLI Detection Core (base detection)
- Story 2: ClaudeCodeNotFoundError (fallback error)
- Story 3: OAuth Login Integration (may use this function)
