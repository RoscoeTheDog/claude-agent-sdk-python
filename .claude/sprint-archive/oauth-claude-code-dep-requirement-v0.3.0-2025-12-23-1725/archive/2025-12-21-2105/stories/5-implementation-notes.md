# Story 5: Implementation Notes

**Completed**: 2025-11-09 17:05
**Duration**: 50 minutes
**Tests Added**: 17 new tests
**Total Tests**: 592 (all passing)

---

## Implementation Summary

Added severity-based filtering for system messages to control visibility based on both render level and message severity.

### Key Components

#### 1. SystemMessageLevel Enum (config.py:35-51)

```python
class SystemMessageLevel(IntEnum):
    """System message severity levels for filtering."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
```

- Defines 5 severity levels
- Ordered from least to most critical
- Used for filtering system messages

#### 2. RendererConfig.min_system_message_level (config.py:65)

```python
min_system_message_level: SystemMessageLevel = SystemMessageLevel.ERROR
```

- Default: `SystemMessageLevel.ERROR` (hides info/warning)
- Configurable per-renderer
- Serializes/deserializes from JSON config files

#### 3. Severity Detection Function (base.py:27-52)

```python
def _detect_system_message_severity(message: SystemMessage) -> SystemMessageLevel:
    """Detect the severity level of a system message."""
    # Parses message.subtype to infer severity
    # Examples:
    # - "critical_error" -> CRITICAL
    # - "error" or "failed" -> ERROR
    # - "warning" -> WARNING
    # - "debug" -> DEBUG
    # - "info" or unknown -> INFO (default)
```

- Pattern-based detection from subtype string
- Case-insensitive matching
- Defaults to INFO for unknown types

#### 4. Updated Handler.should_render() (base.py:246-297)

Filtering logic based on render level:

| Render Level | Minimum Severity Shown |
|--------------|------------------------|
| MINIMAL      | CRITICAL only          |
| STANDARD     | ERROR (configurable via `min_system_message_level`) |
| DETAILED     | DEBUG (all messages)   |
| DEBUG        | DEBUG (all messages)   |
| ALL          | DEBUG (all messages)   |

### Files Modified

1. **src/claude_agent_sdk/rendering/config.py**
   - Added `SystemMessageLevel` enum
   - Added `min_system_message_level` field to `RendererConfig`
   - Updated serialization/deserialization logic

2. **src/claude_agent_sdk/rendering/base.py**
   - Added `_detect_system_message_severity()` helper function
   - Updated `Handler.should_render()` with severity filtering logic

3. **src/claude_agent_sdk/rendering/__init__.py**
   - Exported `SystemMessageLevel` in public API

4. **tests/test_system_message_severity.py** (new file)
   - 17 comprehensive tests covering:
     - Enum values and ordering
     - Severity detection from subtypes
     - Filtering at each render level
     - Custom min_system_message_level configuration
     - Config serialization/deserialization

### Behavior Summary

**Default Behavior (RenderLevel.STANDARD)**:
- Shows: ERROR, CRITICAL
- Hides: DEBUG, INFO, WARNING

**User can customize**:
```python
# Show warnings at STANDARD level
config = RendererConfig(
    render_level=RenderLevel.STANDARD,
    min_system_message_level=SystemMessageLevel.WARNING
)

# Show all messages at DETAILED level (automatic)
config = RendererConfig(render_level=RenderLevel.DETAILED)
```

### Edge Cases Handled

1. **Unknown subtypes**: Default to INFO severity
2. **Case insensitivity**: "ERROR", "error", "Error" all detected as ERROR
3. **Keyword matching**: "operation_failed" detected as ERROR (contains "fail")
4. **Render level priority**: DETAILED/DEBUG/ALL always show all messages regardless of `min_system_message_level`
5. **Serialization**: Handles both string and int values in config files

### Test Coverage

All 17 new tests passing:
- Enum values and comparison operators
- Severity detection for each level
- Filtering behavior at each render level
- Custom configuration scenarios
- Serialization round-trips

Total: 592 tests passing (575 existing + 17 new)

---

## Design Decisions

### 1. Two-Layer Filtering

**Render Level** (outer layer):
- Controls overall detail level
- MINIMAL = show least, ALL = show most
- Existing behavior preserved

**Severity Level** (inner layer, new):
- Fine-grained control for system messages
- Only active when render level allows system messages
- Customizable via `min_system_message_level`

This approach allows:
- Backward compatibility (existing tests still pass)
- Flexible control (users can customize both layers)
- Sensible defaults (ERROR+ at STANDARD level)

### 2. Pattern-Based Detection

Used substring matching instead of exact equality because:
- More flexible (handles variations like "critical_error", "CRITICAL")
- Graceful degradation (unknown -> INFO is safe default)
- Simple to extend (just add more keywords to function)

Alternative considered: explicit severity field on SystemMessage
- Rejected: Would require changing message format
- Current approach infers from existing data

### 3. Default to ERROR (not WARNING)

Reasoning:
- Reduces noise in standard usage
- Matches Story 5 requirement: "hide info/warning by default"
- Users explicitly opt-in to see warnings via config

### 4. DETAILED Shows All

At DETAILED level and above, all system messages are shown regardless of `min_system_message_level`:
- Aligns with "detailed output" expectation
- Existing tests expected this behavior
- Users who want full detail get it automatically

---

## API Examples

### Basic Usage

```python
from claude_agent_sdk.rendering import (
    RendererConfig,
    RenderLevel,
    SystemMessageLevel,
)

# Default: show ERROR+ at STANDARD level
config = RendererConfig()

# Show all system messages
config = RendererConfig(render_level=RenderLevel.DETAILED)

# Show only critical messages
config = RendererConfig(render_level=RenderLevel.MINIMAL)

# Custom: show WARNING+ at STANDARD level
config = RendererConfig(
    render_level=RenderLevel.STANDARD,
    min_system_message_level=SystemMessageLevel.WARNING,
)
```

### Config File

```json
{
  "render_level": "STANDARD",
  "min_system_message_level": "WARNING"
}
```

### Severity Detection

The system automatically detects severity from SystemMessage.subtype:

```python
SystemMessage(subtype="critical_error", data={})  # -> CRITICAL
SystemMessage(subtype="error", data={})           # -> ERROR
SystemMessage(subtype="warning", data={})         # -> WARNING
SystemMessage(subtype="info", data={})            # -> INFO
SystemMessage(subtype="debug", data={})           # -> DEBUG
SystemMessage(subtype="unknown", data={})         # -> INFO (default)
```

---

## Future Enhancements

Potential improvements for later stories:

1. **Explicit severity field**: Add `severity: SystemMessageLevel` to SystemMessage dataclass
2. **Per-severity styling**: Different colors for each severity level
3. **Filtering by subtype patterns**: User-defined regex patterns for custom severity mapping
4. **Count suppression**: "5 INFO messages hidden" indicator
5. **Runtime toggling**: Change min_system_message_level without recreating config

---

**Version**: 1.0
**Last Updated**: 2025-11-09 17:05
