# Implementation Sprint: Pretty Printer - Core Infrastructure

**Created**: 2025-11-05 14:31
**Status**: active
**Sprint Goal**: Implement baseline pretty printer matching Claude Code CLI UTF-8 rendering format with pluggable handler/formatter architecture

---

## Sprint Overview

Create a pluggable, configurable pretty printer system that emulates Claude Code CLI rendering for SDK message output. Sprint 1 focuses on core infrastructure with UTF-8 baseline rendering.

**Key Deliverables**:
- Handler/Formatter abstraction layer (similar to Python logging)
- ClaudeCodeFormatter with exact Claude Code CLI UTF-8 rendering
- StreamHandler (console) + FileHandler (file output)
- Configuration system (RenderLevel, RendererConfig)
- Examples, tests, and documentation

**Architecture**:
```
MessageRenderer
├── Handler (WHERE: console, file, custom)
│   ├── StreamHandler(stdout/stderr)
│   ├── FileHandler(path)
│   └── NullHandler(no-op)
└── Formatter (HOW: format style)
    └── ClaudeCodeFormatter (UTF-8, Claude CLI conventions)
```

**References**:
- Vision doc: `.claude/implementation/archive/2025-11-05-1431/pretty_printer_vision.md`
- Task breakdown: `.claude/implementation/archive/2025-11-05-1431/sprint1_tasks.md`

---

## Stories

### Story 1: Core Abstractions & Configuration
**Status**: completed
**Completed**: 2025-11-05 15:05
**Description**: Create foundational module structure, enums, and configuration classes
**Acceptance Criteria**:
- [x] Module `claude_agent_sdk.rendering` exists and imports cleanly
- [x] `RenderLevel` enum defined with 5 levels (MINIMAL, STANDARD, DETAILED, DEBUG, ALL)
- [x] `RendererConfig` dataclass with all configuration fields
- [x] UTF-8 character defaults match Claude Code CLI (`●`, `⎿`, `→`, `…`, `·`)
- [x] Can create config with defaults: `config = RendererConfig()`

### Story 1.1: Create Module Structure
**Status**: completed
**Claimed**: 2025-11-05 14:45
**Completed**: 2025-11-05 14:47
**Parent**: Story 1
**Description**: Set up directory structure and base files
**Tasks**:
- [x] Create `src/claude_agent_sdk/rendering/` directory
- [x] Create `__init__.py` with placeholder exports
- [x] Create `base.py` for main abstractions
- [x] Create `config.py` for configuration classes

### Story 1.2: Implement RenderLevel Enum
**Status**: completed
**Claimed**: 2025-11-05 14:52
**Completed**: 2025-11-05 14:54
**Parent**: Story 1
**Description**: Define message filtering levels
**Implementation**:
```python
class RenderLevel(IntEnum):
    MINIMAL = 0      # User/assistant text only
    STANDARD = 1     # + tool names, summaries (default)
    DETAILED = 2     # + tool inputs/outputs
    DEBUG = 3        # + system messages
    ALL = 4          # Everything including stream events
```
**Notes**: Implemented in `config.py` with comprehensive docstrings. Exported from `__init__.py`. All 260 existing tests pass.

### Story 1.3: Implement RendererConfig
**Status**: completed
**Claimed**: 2025-11-05 15:02
**Completed**: 2025-11-05 15:05
**Parent**: Story 1
**Description**: Configuration dataclass with UTF-8 defaults
**Key Fields**:
- Display settings (show_metadata, show_tool_inputs, compact_mode)
- Content limits (max_text_length, max_tool_output_length)
- UTF-8 characters (bullet=`●`, tree_connector=`⎿`, arrow=`→`, ellipsis=`…`)
- Filtering (render_level, include/exclude message types)
**Notes**: Implemented in `config.py` with comprehensive field coverage including validation in `__post_init__`. All 260 existing tests pass. Verified all Story 1 parent acceptance criteria are met.

---

### Story 2: Abstract Base Classes
**Status**: completed
**Claimed**: 2025-11-05 15:10
**Completed**: 2025-11-05 15:25
**Description**: Implement Formatter and Handler ABCs with filtering logic
**Acceptance Criteria**:
- [x] `Formatter` ABC defined with abstract methods for each message type
- [x] Helper methods for text truncation and indentation
- [x] `Handler` ABC defined with emit() and should_render()
- [x] `MessageRenderer` class with handler management and thread safety
- [x] Cannot instantiate ABCs directly (raises TypeError)
- [x] All base classes have comprehensive docstrings
**Notes**: Implemented in `base.py` with comprehensive docstrings and type hints. All 260 existing tests pass. Mypy type checking passes. Ruff linting passes.

### Story 2.1: Implement Formatter ABC
**Status**: completed
**Claimed**: 2025-11-05 15:10
**Completed**: 2025-11-05 15:25
**Parent**: Story 2
**Description**: Abstract base class for message formatters
**Methods**:
- `format(message: Message) -> str` - Main entry point
- `format_user_message()`, `format_assistant_message()`, etc. - Type-specific
- `_truncate_text()` - Truncation helper with "… +N lines (ctrl+o to expand)"
- `_indent_lines()` - Indentation helper

### Story 2.2: Implement Handler ABC
**Status**: completed
**Claimed**: 2025-11-05 15:10
**Completed**: 2025-11-05 15:25
**Parent**: Story 2
**Description**: Abstract base class for output handlers
**Methods**:
- `emit(formatted_output: str, message: Message)` - Abstract output method
- `should_render(message: Message) -> bool` - Filtering logic
- `handle(message: Message)` - Orchestration (filter + format + emit)

### Story 2.3: Implement MessageRenderer
**Status**: completed
**Claimed**: 2025-11-05 15:10
**Completed**: 2025-11-05 15:25
**Parent**: Story 2
**Description**: Main rendering coordinator with handler management
**Features**:
- Handler list management (add/remove)
- Thread safety with locks
- `render(message)` dispatches to all handlers
- Error handling (one handler failure doesn't stop others)

---

### Story 3: ClaudeCodeFormatter Implementation
**Status**: completed
**Claimed**: 2025-11-05 15:30
**Completed**: 2025-11-05 15:45
**Description**: Concrete formatter matching Claude Code CLI UTF-8 rendering exactly
**Acceptance Criteria**:
- [x] All message types render correctly
- [x] User messages: `● User: <content>` or `● User answered Claude's questions:`
- [x] Assistant text: `● <text>`
- [x] Tool use: `● <tool>(<param>: <value>)`
- [x] Tool results: `  ⎿  <line1>\n     <line2>\n     … +N lines (ctrl+o to expand)`
- [x] Result messages: `● Result ended\n  Cost: $<amount>`
- [x] Parameters formatted: strings quoted, others not
- [x] Truncation works for long outputs
**Implementation Notes**:
- Created `src/claude_agent_sdk/rendering/formatters.py` with ClaudeCodeFormatter class
- Implemented all abstract methods from Formatter base class
- Added helper methods for tool formatting and parameter value formatting
- Supports JSON serialization for complex parameter types (lists, dicts)
- Uses config UTF-8 characters (●, ⎿, …) from RendererConfig
- All 260 existing tests pass, mypy type checking passes, ruff formatting applied

### Story 3.1: User Message Formatting
**Status**: completed
**Completed**: 2025-11-05 15:45
**Parent**: Story 3
**Description**: Format UserMessage with simple and structured content
**Formats**:
- Simple: `● User: <text>`
- Structured (questions): Multi-line with `⎿` and `·` bullets

### Story 3.2: Assistant Message Formatting
**Status**: completed
**Completed**: 2025-11-05 15:45
**Parent**: Story 3
**Description**: Format AssistantMessage with text and tool blocks
**Formats**:
- Text blocks: `● <text>`
- Tool use blocks: `● <tool>(<params>)`
- Thinking blocks: `● <thinking text>` (basic, can enhance later)

### Story 3.3: Tool Formatting
**Status**: completed
**Completed**: 2025-11-05 15:45
**Parent**: Story 3
**Description**: Format ToolUseBlock and ToolResultBlock
**ToolUseBlock**:
- Format: `● <name>(<key>: "value", <key>: value)`
- String params quoted, others not
- Detect MCP tools (optional: add "(MCP)" label)

**ToolResultBlock**:
- Format: `  ⎿  <first line>\n     <continuation>`
- Truncation: `… +N lines (ctrl+o to expand)`
- Error handling: Prefix with "ERROR:" if `is_error=True`

### Story 3.4: System & Result Message Formatting
**Status**: completed
**Completed**: 2025-11-05 15:45
**Parent**: Story 3
**Description**: Format SystemMessage and ResultMessage
**SystemMessage**: Basic bullet format (only in DEBUG+ levels)
**ResultMessage**:
```
● Result ended
  Cost: $<total_cost_usd>
```

### Story 3.5: Stream Event Formatting
**Status**: completed
**Completed**: 2025-11-05 15:45
**Parent**: Story 3
**Description**: Format StreamEvent (partial messages)
**Approach**: Basic rendering for Sprint 1, defer incremental updates to Sprint 2

---

### Story 4: Handler Implementations
**Status**: completed
**Claimed**: 2025-11-05 15:50
**Completed**: 2025-11-05 16:00
**Description**: Implement concrete handlers for console and file output
**Acceptance Criteria**:
- [x] `StreamHandler` writes to stdout/stderr with UTF-8 encoding
- [x] `FileHandler` creates files with parent directories, UTF-8 encoding
- [x] `NullHandler` does nothing (for testing/silencing)
- [x] All handlers respect filtering (should_render)
- [x] Error handling for I/O failures
**Implementation Notes**:
- Created `src/claude_agent_sdk/rendering/handlers.py` with all three handler classes
- StreamHandler: Configurable stream (default stdout), auto-flush option, UTF-8 encoding via reconfigure
- FileHandler: Path.open() for proper typing, parent directory creation, proper file handle cleanup
- NullHandler: Simple no-op implementation for testing
- All handlers exported from `__init__.py`
- All 260 existing tests pass, mypy type checking passes, ruff formatting applied

### Story 4.1: StreamHandler
**Status**: completed
**Completed**: 2025-11-05 16:00
**Parent**: Story 4
**Description**: Console output handler
**Features**:
- Default to stdout
- Support stderr or custom stream
- UTF-8 encoding via `stream.reconfigure(encoding='utf-8')`
- Auto-flush option
- Double newline between messages (Claude Code CLI convention)

### Story 4.2: FileHandler
**Status**: completed
**Completed**: 2025-11-05 16:00
**Parent**: Story 4
**Description**: File output handler
**Features**:
- Accept filepath (str or Path)
- Append mode (default) or overwrite
- Create parent directories if missing
- UTF-8 encoding
- Proper file handle cleanup (__del__ and close())

### Story 4.3: NullHandler
**Status**: completed
**Completed**: 2025-11-05 16:00
**Parent**: Story 4
**Description**: No-op handler for testing
**Implementation**: emit() does nothing, always returns successfully

---

### Story 5: Integration & Examples
**Status**: completed
**Claimed**: 2025-11-05 16:05
**Completed**: 2025-11-05 16:15
**Description**: Package exports, examples, and convenience functions
**Acceptance Criteria**:
- [x] All public classes exported from `claude_agent_sdk.rendering`
- [x] Example `examples/pretty_printer_basic.py` works
- [x] Convenience function `display_message()` available
- [x] Example shows console + file output simultaneously
- [x] Easy migration from old `examples/streaming_mode.py` pattern
**Implementation Notes**:
- Added `display_message()` convenience function with singleton pattern
- Created comprehensive example with three usage patterns:
  1. Simple usage with display_message()
  2. Multi-handler setup (console + file)
  3. Custom configuration
- All code linted and formatted with ruff
- Type checking passes with mypy

### Story 5.1: Package Exports
**Status**: completed
**Completed**: 2025-11-05 16:10
**Parent**: Story 5
**Description**: Update `__init__.py` files with public API
**Exports**:
- `MessageRenderer`
- `RenderLevel`, `RendererConfig`
- `ClaudeCodeFormatter`
- `StreamHandler`, `FileHandler`, `NullHandler`
- `display_message()` convenience function
**Notes**: All classes already exported. Added `display_message()` convenience function with singleton renderer pattern.

### Story 5.2: Create Basic Example
**Status**: completed
**Completed**: 2025-11-05 16:15
**Parent**: Story 5
**Description**: `examples/pretty_printer_basic.py` demonstrating usage
**Shows**:
- Console rendering (minimal level)
- File rendering (detailed level)
- Multi-handler setup
- Real SDK integration
**Notes**: Created comprehensive example with three patterns: simple display_message(), multi-handler, and custom config.

### Story 5.3: Convenience Function
**Status**: completed
**Completed**: 2025-11-05 16:10
**Parent**: Story 5
**Description**: Add `display_message()` helper for quick usage
**Implementation**: Singleton renderer, lazy initialization, simple API
**Notes**: Implemented in `__init__.py` with proper type hints. Uses global singleton pattern with lazy initialization.

---

### Story 6: Testing
**Status**: completed
**Claimed**: 2025-11-05 16:20
**Completed**: 2025-11-05 16:45
**Description**: Comprehensive unit tests for all components
**Acceptance Criteria**:
- [x] Tests for `RenderLevel` and `RendererConfig`
- [x] Tests for `MessageRenderer` handler management
- [x] Tests for `ClaudeCodeFormatter` with all message types
- [x] Tests for all handlers (Stream, File, Null)
- [x] Tests for filtering logic (include/exclude, levels)
- [x] Code coverage >80% for rendering module
- [x] All edge cases covered (empty content, None values, errors)
**Implementation Notes**:
- Created `test_rendering_config.py` with 15 tests for RenderLevel and RendererConfig
- Created `test_rendering_formatters.py` with 34 tests for ClaudeCodeFormatter
- Created `test_rendering_handlers.py` with 24 tests for all handlers and MessageRenderer
- Created `test_rendering_integration.py` with 13 integration tests
- Total: 86 new tests, all passing
- All 346 SDK tests pass (260 existing + 86 new)
- No regressions in existing functionality

### Story 6.1: Configuration Tests
**Status**: completed
**Completed**: 2025-11-05 16:30
**Parent**: Story 6
**Description**: Test config classes and enums
**Tests**:
- RenderLevel comparison and ordering
- RendererConfig defaults
- RendererConfig field overrides
- UTF-8 character defaults
**Notes**: 15 tests created in test_rendering_config.py, all passing

### Story 6.2: Formatter Tests
**Status**: completed
**Completed**: 2025-11-05 16:35
**Parent**: Story 6
**Description**: Test ClaudeCodeFormatter rendering
**Test Cases**:
- User message simple: `"● User: Hello"`
- Tool use: `'● Read(file_path: "test.py", limit: 100)'`
- Tool result truncation with ctrl+o indicator
- Empty content handling
- Parameter quoting (strings vs non-strings)
**Notes**: 34 tests created in test_rendering_formatters.py, all passing

### Story 6.3: Handler Tests
**Status**: completed
**Completed**: 2025-11-05 16:40
**Parent**: Story 6
**Description**: Test handler behavior
**Tests**:
- StreamHandler writes to stdout
- FileHandler creates file with correct encoding
- Filtering respects include/exclude lists
- Error in one handler doesn't affect others
**Notes**: 24 tests created in test_rendering_handlers.py, all passing

### Story 6.4: Integration Tests
**Status**: completed
**Completed**: 2025-11-05 16:45
**Parent**: Story 6
**Description**: Test with real SDK messages
**Tests**:
- Real ClaudeSDKClient messages
- UTF-8 renders correctly in terminal
- No regressions in existing SDK tests
**Notes**: 13 integration tests created in test_rendering_integration.py, all passing. Verified all 346 SDK tests pass.

---

### Story 7: Documentation
**Status**: completed
**Claimed**: 2025-11-05 16:50
**Completed**: 2025-11-05 17:00
**Description**: Docstrings, usage guide, and README updates
**Acceptance Criteria**:
- [x] All public classes have docstrings
- [x] All public methods have docstrings with examples
- [x] Usage guide created: `docs/rendering.md`
- [x] README updated with rendering section
- [x] Code examples in docstrings
- [x] API reference complete
**Notes**: All documentation completed. Docstrings were already comprehensive from earlier stories. Created extensive 500+ line usage guide in docs/rendering.md covering all features, examples, and API reference. Added rendering section to README with quick start, multiple destinations, and render levels examples.

### Story 7.1: Docstrings
**Status**: completed
**Completed**: 2025-11-05 16:55
**Parent**: Story 7
**Description**: Add comprehensive docstrings to all public APIs
**Include**: Class purpose, parameters, return values, examples
**Notes**: All docstrings were already in place from Stories 1-6. Verified coverage of all public classes and methods with examples.

### Story 7.2: Usage Guide
**Status**: completed
**Completed**: 2025-11-05 16:58
**Parent**: Story 7
**Description**: Create `docs/rendering.md` with examples
**Sections**:
- Quick Start
- Architecture Overview
- Configuration Options
- Custom Formatters (how to extend)
- Custom Handlers (how to extend)
- Examples
- API Reference
**Notes**: Created comprehensive 500+ line documentation covering all sections plus thread safety, error handling, performance considerations, and future enhancements.

### Story 7.3: Update README
**Status**: completed
**Completed**: 2025-11-05 17:00
**Parent**: Story 7
**Description**: Add rendering section to main README
**Content**: Quick example, link to full docs, migration note
**Notes**: Added Message Rendering section with quick start example, multiple destinations example, render levels list, and link to full documentation.

---

### Story 8: Polish & Completion
**Status**: unassigned
**Description**: Final cleanup, git commit, and sprint summary
**Acceptance Criteria**:
- [ ] All tests passing
- [ ] No regressions in existing SDK functionality
- [ ] Code formatted with ruff
- [ ] Type checking passes (mypy)
- [ ] Git commit with all changes
- [ ] Sprint summary completed

### Story 8.1: Code Quality
**Status**: unassigned
**Parent**: Story 8
**Description**: Run linters and type checkers
**Commands**:
```bash
python -m ruff check src/ tests/ --fix
python -m ruff format src/ tests/
python -m mypy src/
python -m pytest tests/
```

### Story 8.2: Git Commit
**Status**: unassigned
**Parent**: Story 8
**Description**: Commit all changes
**Message**: `feat: Add pretty printer with Claude Code CLI rendering`

### Story 8.3: Sprint Summary
**Status**: unassigned
**Parent**: Story 8
**Description**: Complete sprint summary section in this document

---

## Progress Log

### 2025-11-05 14:31 - Sprint Started
- Created sprint structure
- Archived previous planning docs to `archive/2025-11-05-1431/`
- Defined 8 major stories with 28 sub-stories
- Sprint goal: Core pretty printer infrastructure matching Claude Code CLI UTF-8 rendering

---

## Sprint Summary
_(To be filled upon completion)_

**Final Metrics**:
- Stories completed: _/8
- Sub-stories completed: _/28
- Tests added: _
- Code coverage: _%
- Files changed: _

**Key Achievements**:
- _TBD_

**Lessons Learned**:
- _TBD_

**Next Steps** (Sprint 2+):
- Rich formatting with colors
- Metadata display
- Interactive features
