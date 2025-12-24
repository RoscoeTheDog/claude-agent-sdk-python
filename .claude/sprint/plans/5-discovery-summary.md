# Story 5.d Discovery Summary

**Status**: ✅ Completed
**Date**: 2025-12-21

## Quick Overview

Analyzed test coverage for cross-platform CLI detection. Found **strong foundation** with some targeted gaps to address.

## Current Coverage: 85-90%

### ✅ What's Well Tested
- PATH detection via `shutil.which`
- Platform-specific paths (Windows .exe/.cmd, macOS Homebrew, Linux system paths)
- Error message structure and content
- Auto-install workflow (success and failure cases)
- Windows environment variable handling (LOCALAPPDATA/APPDATA)

### ⚠️ Gaps to Address

#### P0 (Critical - Must Fix)
1. **Exhaustive path coverage**: Only 7 of 11+ fallback paths tested
   - Missing: `.yarn/bin/claude`, `.claude/local/claude`
   - Missing: Cross-verification of all paths in implementation
2. **Error message dynamic content**: Not validating actual searched paths in error output

#### P1 (Important - Should Fix)
1. **Test maintainability**: Path mocking is complex and fragile (nested lambdas)
2. **Path priority order**: Not testing that first-found wins
3. **Environment variable edge cases**: What if LOCALAPPDATA not set?

#### P2 (Nice-to-Have)
1. **Integration tests**: No tests against real CLI binary
2. **CI multi-platform**: Not testing on actual Windows/macOS/Linux in CI
3. **Edge cases**: Symlinks, permissions, unicode paths

## Test Strategy

### Simplify Path Mocking
Replace complex lambda-based mocks with pytest fixtures:
```python
@pytest.fixture
def mock_platform_paths(platform_name, existing_paths):
    """Create consistent path mocks for testing"""
    # Centralized, maintainable path mocking
```

### Parameterized Platform Tests
```python
@pytest.mark.parametrize("platform,path,exists", [
    ("Windows", "AppData/Local/npm/claude.cmd", True),
    ("Darwin", "/opt/homebrew/bin/claude", True),
    # ... all 11+ paths
])
def test_all_fallback_locations(platform, path, exists):
    """Verify every fallback path works"""
```

### Optional Integration Testing
```python
@pytest.mark.skipif(not os.getenv("CLAUDE_CLI_INTEGRATION_TEST"))
def test_with_real_cli():
    """Run against actual installed CLI if available"""
```

## File Changes Required

| File | Changes | Lines | Type |
|------|---------|-------|------|
| `test_cli_detection.py` | Add exhaustive path tests | +105 | Modify |
| `test_errors.py` | Validate dynamic error content | +45 | Modify |
| `conftest.py` | Shared path mocking fixtures | +80 | New |
| `test_integration.py` | Real CLI tests (optional) | +60 | New |
| `.github/workflows/` | CI matrix for platforms | +30 | New/Modify |

**Total**: ~280 new lines, ~50 modified lines

## Implementation Plan (Story 5.i)

### Phase 1: P0 Fixes (2-3 hours)
1. Create `conftest.py` with simplified path fixtures
2. Add parameterized test for all 11+ fallback paths
3. Validate error message contains searched paths

### Phase 2: P1 Improvements (1-2 hours)
1. Refactor existing tests to use new fixtures
2. Add path priority order test
3. Test environment variable edge cases

### Phase 3: P2 Enhancements (1-2 hours, optional)
1. Create `test_integration.py` with real CLI tests
2. Add CI workflow for multi-platform testing
3. Add edge case tests (symlinks, permissions)

## Success Metrics

- ✅ All 11+ fallback paths have explicit tests
- ✅ Error messages validated for dynamic content
- ✅ Test coverage >= 95% for `cli_detection.py`
- ✅ Tests pass on Windows/macOS/Linux (manual or CI)
- ✅ Path mocking complexity reduced (maintainability)

## Key Findings

### Strengths
- Existing tests are thorough for core functionality
- Platform awareness already baked in
- Error handling well covered
- Good separation of detection vs error tests

### Opportunities
- **Maintainability**: Current mocks are fragile, hard to debug
- **Completeness**: Missing 4 fallback paths, edge cases
- **Confidence**: No integration tests, all mocked
- **CI**: Not leveraging multi-platform testing

### Risk Assessment
- **Low Risk**: Core detection logic is well tested
- **Medium Risk**: Edge cases could bite production users
- **Low Risk**: Missing paths unlikely to affect most users (niche install methods)

## Next Steps

1. **Story 5.i (Implementation)**: Address P0 and P1 gaps
2. **Story 5.v (Validation)**: Run tests on all platforms, verify coverage
3. **Optional**: Add P2 enhancements if time permits

## References

- Implementation: `src/claude_agent_sdk/_internal/cli_detection.py` (192 lines)
- Current tests: `tests/test_cli_detection.py` (519 lines)
- Error tests: `tests/test_errors.py` (205 lines)
- Full plan: `.claude/sprint/plans/5-plan.yaml`
