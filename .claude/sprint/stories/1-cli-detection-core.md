# Story 1: CLI Detection Core

**Status**: unassigned
**Created**: 2025-12-21 21:37

## Description

Create the core CLI detection module with multi-path search functionality. This implements Approach F from the handoff spec - detecting existing Claude Code CLI installations across multiple locations.

## Acceptance Criteria

- [ ] (P0) `find_claude_cli()` function detects Claude CLI in PATH via `shutil.which('claude')`
- [ ] (P0) Function checks `~/.claude/bin/claude` local installation path
- [ ] (P1) Function checks platform-specific paths (Homebrew on macOS, AppData on Windows, .local/bin on Linux)
- [ ] (P0) Returns absolute path to claude executable when found
- [ ] (P1) Handles Windows .exe/.cmd extensions correctly

## Dependencies

None

## Implementation Notes

*To be added during implementation*

## Related Stories

- Story 2: ClaudeCodeNotFoundError (uses this detection)
- Story 3: OAuth Login Integration (integrates this module)
