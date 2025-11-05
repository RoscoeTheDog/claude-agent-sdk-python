# Sprint 1: Core Renderer Infrastructure - Task Breakdown

**Goal**: Implement baseline pretty printer matching Claude Code CLI UTF-8 rendering format
**Duration**: Short sprint (targeting completion in 1-2 sessions)

---

## Task List

### Phase 1: Core Abstractions (Foundation)

#### Task 1.1: Create rendering module structure
- [ ] Create `src/claude_agent_sdk/rendering/` directory
- [ ] Create `__init__.py` with public API exports
- [ ] Create `base.py` with abstract classes
- [ ] Add module to package exports

**Files**:
- `src/claude_agent_sdk/rendering/__init__.py`
- `src/claude_agent_sdk/rendering/base.py`

**Acceptance Criteria**:
- Module can be imported: `from claude_agent_sdk.rendering import MessageRenderer`
- No implementation yet, just scaffolding

---

#### Task 1.2: Implement RenderLevel enum
- [ ] Create `config.py` with `RenderLevel` enum
- [ ] Add docstrings explaining each level
- [ ] Export from `__init__.py`

**Code**:
```python
# src/claude_agent_sdk/rendering/config.py
from enum import IntEnum

class RenderLevel(IntEnum):
    """Control verbosity of message rendering."""
    MINIMAL = 0      # Only user/assistant text
    STANDARD = 1     # + tool names, result summaries (default)
    DETAILED = 2     # + tool inputs/outputs
    DEBUG = 3        # + system messages
    ALL = 4          # Everything including stream events
```

**Acceptance Criteria**:
- Can import and use: `RenderLevel.STANDARD`
- Integer comparison works: `RenderLevel.DEBUG > RenderLevel.MINIMAL`

---

#### Task 1.3: Implement RendererConfig dataclass
- [ ] Add `RendererConfig` to `config.py`
- [ ] Add all configuration fields with defaults
- [ ] Add validation logic (if needed)
- [ ] Export from `__init__.py`

**Code Skeleton**:
```python
from dataclasses import dataclass

@dataclass
class RendererConfig:
    """Configuration for message rendering behavior."""

    # Display settings
    show_metadata: bool = False
    show_tool_inputs: bool = False
    show_tool_outputs: bool = True
    compact_mode: bool = False

    # Content limits
    max_text_length: int | None = None
    max_tool_output_length: int = 500
    truncation_indicator: str = "… +{count} lines (ctrl+o to expand)"

    # Filtering
    render_level: RenderLevel = RenderLevel.STANDARD
    include_message_types: list[type] | None = None
    exclude_message_types: list[type] | None = None

    # Character set (UTF-8 by default)
    bullet: str = "●"           # U+25CF
    tree_connector: str = "⎿"   # U+23BF
    arrow: str = "→"            # U+2192
    ellipsis: str = "…"         # U+2026
    list_dot: str = "·"         # U+00B7

    # Indentation
    indent_size: int = 2
    tree_indent_size: int = 3   # Indent after ⎿
```

**Acceptance Criteria**:
- Can create with defaults: `config = RendererConfig()`
- Can override fields: `config = RendererConfig(show_metadata=True)`
- UTF-8 characters match Claude Code CLI

---

### Phase 2: Abstract Base Classes

#### Task 2.1: Implement Formatter ABC
- [ ] Create `formatters/base_formatter.py`
- [ ] Define `Formatter` abstract base class
- [ ] Add abstract methods for each message type
- [ ] Add helper methods for common formatting tasks

**Code Skeleton**:
```python
from abc import ABC, abstractmethod
from claude_agent_sdk.types import (
    Message, UserMessage, AssistantMessage,
    SystemMessage, ResultMessage, StreamEvent,
    ToolUseBlock, ToolResultBlock, TextBlock
)
from ..config import RendererConfig

class Formatter(ABC):
    """Abstract base class for message formatters."""

    def __init__(self, config: RendererConfig | None = None):
        self.config = config or RendererConfig()

    @abstractmethod
    def format(self, message: Message) -> str:
        """Format a message for display."""
        pass

    @abstractmethod
    def format_user_message(self, msg: UserMessage) -> str:
        """Format a user message."""
        pass

    @abstractmethod
    def format_assistant_message(self, msg: AssistantMessage) -> str:
        """Format an assistant message."""
        pass

    # ... other abstract methods for each message type

    # Helper methods (concrete)
    def _truncate_text(self, text: str, max_length: int | None) -> str:
        """Truncate text with ellipsis if over max_length."""
        if max_length is None or len(text) <= max_length:
            return text

        lines = text.split('\n')
        if len(lines) > max_length:
            visible_lines = lines[:max_length]
            hidden_count = len(lines) - max_length
            truncation = self.config.truncation_indicator.format(count=hidden_count)
            return '\n'.join(visible_lines) + '\n' + truncation
        return text

    def _indent_lines(self, text: str, indent: str) -> str:
        """Add indentation to all lines."""
        lines = text.split('\n')
        return '\n'.join(indent + line if line else '' for line in lines)
```

**Acceptance Criteria**:
- Cannot instantiate `Formatter` directly (ABC)
- Subclasses must implement all abstract methods
- Helper methods work correctly

---

#### Task 2.2: Implement Handler ABC
- [ ] Create `handlers/base.py`
- [ ] Define `Handler` abstract base class
- [ ] Add filtering logic
- [ ] Add level checking

**Code Skeleton**:
```python
from abc import ABC, abstractmethod
from claude_agent_sdk.types import Message
from ..config import RenderLevel
from ..formatters.base_formatter import Formatter

class Handler(ABC):
    """Abstract base class for output handlers."""

    def __init__(
        self,
        formatter: Formatter,
        level: RenderLevel = RenderLevel.ALL,
    ):
        self.formatter = formatter
        self.level = level

    @abstractmethod
    def emit(self, formatted_output: str, message: Message) -> None:
        """Write formatted output to destination."""
        pass

    def should_render(self, message: Message) -> bool:
        """Determine if message should be rendered based on level/filters."""
        # Check message type against config filters
        config = self.formatter.config

        # Include/exclude filtering
        if config.include_message_types:
            if type(message) not in config.include_message_types:
                return False

        if config.exclude_message_types:
            if type(message) in config.exclude_message_types:
                return False

        # Level-based filtering
        # (implementation depends on message type -> level mapping)
        return True

    def handle(self, message: Message) -> None:
        """Process and emit a message if it should be rendered."""
        if not self.should_render(message):
            return

        formatted = self.formatter.format(message)
        if formatted:  # Only emit if there's content
            self.emit(formatted, message)
```

**Acceptance Criteria**:
- Cannot instantiate `Handler` directly (ABC)
- `should_render()` respects filters
- `handle()` orchestrates filtering + formatting + emission

---

#### Task 2.3: Implement MessageRenderer
- [ ] Create `MessageRenderer` class in `base.py`
- [ ] Add handler management (add/remove)
- [ ] Implement `render()` method
- [ ] Add thread safety (locks)

**Code Skeleton**:
```python
import threading
from claude_agent_sdk.types import Message
from .handlers.base import Handler

class MessageRenderer:
    """Main rendering coordinator. Dispatches messages to handlers."""

    def __init__(self, handlers: list[Handler] | None = None):
        self._handlers: list[Handler] = handlers or []
        self._lock = threading.Lock()

    def add_handler(self, handler: Handler) -> None:
        """Add a handler to the renderer."""
        with self._lock:
            if handler not in self._handlers:
                self._handlers.append(handler)

    def remove_handler(self, handler: Handler) -> None:
        """Remove a handler from the renderer."""
        with self._lock:
            if handler in self._handlers:
                self._handlers.remove(handler)

    def render(self, message: Message) -> None:
        """Render a message using all registered handlers."""
        # Read-only snapshot to avoid holding lock during rendering
        with self._lock:
            handlers = self._handlers.copy()

        for handler in handlers:
            try:
                handler.handle(message)
            except Exception as e:
                # Log error but don't crash - other handlers should still work
                # TODO: Add proper logging
                print(f"Error rendering message with {handler}: {e}", file=sys.stderr)
```

**Acceptance Criteria**:
- Can add/remove handlers safely
- `render()` dispatches to all handlers
- Errors in one handler don't affect others
- Thread-safe for concurrent access

---

### Phase 3: Concrete Implementations

#### Task 3.1: Implement ClaudeCodeFormatter (BaseFormatter)
- [ ] Create `formatters/claude_code_formatter.py`
- [ ] Implement all abstract methods from `Formatter`
- [ ] Match Claude Code CLI UTF-8 rendering exactly
- [ ] Handle all message types and content blocks

**Implementation Details**:

**User Messages**:
```python
def format_user_message(self, msg: UserMessage) -> str:
    """
    Format:
    ● User: <content>

    Or for structured content:
    ● User answered Claude's questions:
      ⎿  · <question> → <answer>
    """
    bullet = self.config.bullet

    if isinstance(msg.content, str):
        return f"{bullet} User: {msg.content}"

    # Handle list of content blocks
    # ... (check for tool results indicating question answers)
```

**Assistant Messages**:
```python
def format_assistant_message(self, msg: AssistantMessage) -> str:
    """
    Format:
    ● <text content>

    ● <tool-name>(<params>)
      ⎿  <result>
    """
    bullet = self.config.bullet
    tree = self.config.tree_connector

    output_lines = []

    for block in msg.content:
        if isinstance(block, TextBlock):
            output_lines.append(f"{bullet} {block.text}")

        elif isinstance(block, ToolUseBlock):
            # Format: ● <name>(<params>)
            tool_line = self._format_tool_use(block)
            output_lines.append(tool_line)

    return '\n\n'.join(output_lines)
```

**Tool Use Formatting**:
```python
def _format_tool_use(self, block: ToolUseBlock) -> str:
    """
    Format tool use block:
    ● <tool-name>(<param>: <value>, <param>: <value>)
    """
    bullet = self.config.bullet

    # Format parameters
    params = []
    for key, value in block.input.items():
        if isinstance(value, str):
            params.append(f'{key}: "{value}"')
        else:
            params.append(f'{key}: {value}')

    params_str = ', '.join(params)
    return f"{bullet} {block.name}({params_str})"
```

**Tool Result Formatting**:
```python
def _format_tool_result(self, block: ToolResultBlock, parent_tool_name: str = "") -> str:
    """
    Format tool result:
      ⎿  <result line 1>
         <result line 2>
         … +N lines (ctrl+o to expand)
    """
    tree = self.config.tree_connector
    indent = ' ' * self.config.tree_indent_size

    content = block.content
    if isinstance(content, str):
        lines = content.split('\n')
    else:
        # Handle list of content blocks
        lines = [str(content)]

    # Apply truncation
    max_lines = self.config.max_tool_output_length
    if max_lines and len(lines) > max_lines:
        visible_lines = lines[:max_lines]
        hidden_count = len(lines) - max_lines
        truncation = self.config.truncation_indicator.format(count=hidden_count)
        lines = visible_lines + [truncation]

    # Format with tree connector
    if not lines:
        return f"  {tree}  <empty result>"

    first_line = f"  {tree}  {lines[0]}"
    other_lines = [f"  {indent}{line}" for line in lines[1:]]

    return '\n'.join([first_line] + other_lines)
```

**Acceptance Criteria**:
- All message types render correctly
- Output matches Claude Code CLI format character-for-character
- Truncation works for long outputs
- Parameters formatted correctly (strings quoted, others not)

---

#### Task 3.2: Implement StreamHandler
- [ ] Create `handlers/stream_handler.py`
- [ ] Support stdout/stderr streams
- [ ] Add flush control
- [ ] Handle encoding properly (UTF-8)

**Code**:
```python
import sys
from typing import TextIO
from claude_agent_sdk.types import Message
from .base import Handler
from ..formatters.base_formatter import Formatter
from ..config import RenderLevel

class StreamHandler(Handler):
    """Handler that writes to a stream (stdout/stderr)."""

    def __init__(
        self,
        formatter: Formatter,
        stream: TextIO | None = None,
        level: RenderLevel = RenderLevel.ALL,
        auto_flush: bool = True,
    ):
        super().__init__(formatter, level)
        self.stream = stream or sys.stdout
        self.auto_flush = auto_flush

        # Ensure UTF-8 encoding
        if hasattr(self.stream, 'reconfigure'):
            try:
                self.stream.reconfigure(encoding='utf-8')
            except:
                pass  # Some streams don't support reconfigure

    def emit(self, formatted_output: str, message: Message) -> None:
        """Write formatted output to the stream."""
        try:
            self.stream.write(formatted_output)
            self.stream.write('\n\n')  # Claude Code uses double newlines between items

            if self.auto_flush:
                self.stream.flush()

        except Exception as e:
            # Fallback: try stderr if stdout fails
            if self.stream is not sys.stderr:
                sys.stderr.write(f"StreamHandler error: {e}\n")
```

**Acceptance Criteria**:
- Writes to stdout by default
- Can specify stderr or custom stream
- UTF-8 encoding configured
- Auto-flush works

---

#### Task 3.3: Implement FileHandler
- [ ] Create `handlers/file_handler.py`
- [ ] Support file paths
- [ ] Add append/overwrite modes
- [ ] Handle file errors gracefully
- [ ] Ensure UTF-8 encoding

**Code**:
```python
from pathlib import Path
from typing import TextIO
from claude_agent_sdk.types import Message
from .base import Handler
from ..formatters.base_formatter import Formatter
from ..config import RenderLevel

class FileHandler(Handler):
    """Handler that writes to a file."""

    def __init__(
        self,
        formatter: Formatter,
        filepath: str | Path,
        mode: str = 'a',  # 'a' for append, 'w' for overwrite
        level: RenderLevel = RenderLevel.ALL,
        encoding: str = 'utf-8',
    ):
        super().__init__(formatter, level)
        self.filepath = Path(filepath)
        self.mode = mode
        self.encoding = encoding
        self._file: TextIO | None = None
        self._open_file()

    def _open_file(self) -> None:
        """Open the file for writing."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            self._file = open(self.filepath, self.mode, encoding=self.encoding)
        except Exception as e:
            import sys
            sys.stderr.write(f"FileHandler error opening {self.filepath}: {e}\n")
            self._file = None

    def emit(self, formatted_output: str, message: Message) -> None:
        """Write formatted output to the file."""
        if self._file is None:
            return

        try:
            self._file.write(formatted_output)
            self._file.write('\n\n')
            self._file.flush()
        except Exception as e:
            import sys
            sys.stderr.write(f"FileHandler emit error: {e}\n")

    def close(self) -> None:
        """Close the file handle."""
        if self._file:
            try:
                self._file.close()
            except:
                pass
            self._file = None

    def __del__(self):
        """Ensure file is closed on deletion."""
        self.close()
```

**Acceptance Criteria**:
- Creates file if doesn't exist
- Creates parent directories if needed
- Append mode works (default)
- Overwrite mode works
- UTF-8 encoding set
- Closes file properly

---

#### Task 3.4: Implement NullHandler
- [ ] Create `handlers/null_handler.py`
- [ ] No-op implementation (for testing/silence)

**Code**:
```python
from claude_agent_sdk.types import Message
from .base import Handler

class NullHandler(Handler):
    """Handler that does nothing (useful for testing or selective silencing)."""

    def emit(self, formatted_output: str, message: Message) -> None:
        """Do nothing."""
        pass
```

**Acceptance Criteria**:
- Can be instantiated
- `emit()` does nothing
- No errors or side effects

---

### Phase 4: Integration & Examples

#### Task 4.1: Update package exports
- [ ] Export all public classes from `rendering/__init__.py`
- [ ] Add to main package `__init__.py`

**Code**:
```python
# src/claude_agent_sdk/rendering/__init__.py
from .base import MessageRenderer
from .config import RenderLevel, RendererConfig
from .formatters.claude_code_formatter import ClaudeCodeFormatter
from .handlers.stream_handler import StreamHandler
from .handlers.file_handler import FileHandler
from .handlers.null_handler import NullHandler

__all__ = [
    'MessageRenderer',
    'RenderLevel',
    'RendererConfig',
    'ClaudeCodeFormatter',
    'StreamHandler',
    'FileHandler',
    'NullHandler',
]
```

**Acceptance Criteria**:
- Can import: `from claude_agent_sdk.rendering import MessageRenderer`
- All public classes accessible

---

#### Task 4.2: Create basic usage example
- [ ] Create `examples/pretty_printer_basic.py`
- [ ] Show console rendering
- [ ] Show file rendering
- [ ] Show multi-handler setup

**Example Code**:
```python
#!/usr/bin/env python3
"""Basic example of using the pretty printer."""

import asyncio
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.rendering import (
    MessageRenderer,
    StreamHandler,
    FileHandler,
    ClaudeCodeFormatter,
    RendererConfig,
    RenderLevel,
)

async def main():
    # Setup renderer with console output
    renderer = MessageRenderer()

    # Console handler - minimal output
    console_formatter = ClaudeCodeFormatter(
        config=RendererConfig(render_level=RenderLevel.MINIMAL)
    )
    renderer.add_handler(StreamHandler(formatter=console_formatter))

    # File handler - detailed output
    file_formatter = ClaudeCodeFormatter(
        config=RendererConfig(
            render_level=RenderLevel.DETAILED,
            show_metadata=True,
        )
    )
    renderer.add_handler(FileHandler(
        formatter=file_formatter,
        filepath="conversation.log"
    ))

    # Run query
    async with ClaudeSDKClient() as client:
        await client.query("What is 2+2?")

        async for msg in client.receive_response():
            renderer.render(msg)

if __name__ == "__main__":
    asyncio.run(main())
```

**Acceptance Criteria**:
- Example runs without errors
- Console shows minimal output
- File contains detailed output
- Output matches Claude Code CLI format

---

#### Task 4.3: Add convenience function (migration helper)
- [ ] Add `display_message()` helper to `rendering/__init__.py`
- [ ] Make it easy to migrate from old `examples/streaming_mode.py` pattern

**Code**:
```python
# In rendering/__init__.py

# Convenience singleton for quick starts
_default_renderer: MessageRenderer | None = None

def display_message(message: Message, config: RendererConfig | None = None) -> None:
    """
    Convenience function for quick message rendering to console.

    Usage:
        async for msg in client.receive_response():
            display_message(msg)

    This creates a singleton renderer on first call.
    For more control, use MessageRenderer directly.
    """
    global _default_renderer

    if _default_renderer is None:
        formatter = ClaudeCodeFormatter(config=config or RendererConfig())
        handler = StreamHandler(formatter=formatter)
        _default_renderer = MessageRenderer(handlers=[handler])

    _default_renderer.render(message)
```

**Acceptance Criteria**:
- Can call `display_message(msg)` directly
- Creates renderer on first call (lazy)
- Reuses renderer on subsequent calls
- Easy migration from old pattern

---

### Phase 5: Testing & Documentation

#### Task 5.1: Write unit tests
- [ ] Test `RendererConfig` defaults and validation
- [ ] Test `MessageRenderer` handler management
- [ ] Test `ClaudeCodeFormatter` with all message types
- [ ] Test `StreamHandler` output
- [ ] Test `FileHandler` file creation and writing
- [ ] Test filtering logic (include/exclude types, levels)

**Test Files**:
- `tests/rendering/test_config.py`
- `tests/rendering/test_renderer.py`
- `tests/rendering/test_formatters.py`
- `tests/rendering/test_handlers.py`

**Key Test Cases**:
```python
def test_user_message_simple():
    """Test simple user message matches Claude Code CLI format."""
    msg = UserMessage(content="Hello world")
    formatter = ClaudeCodeFormatter()
    result = formatter.format_user_message(msg)
    assert result == "● User: Hello world"

def test_tool_use_formatting():
    """Test tool use matches Claude Code CLI format."""
    tool = ToolUseBlock(
        id="123",
        name="Read",
        input={"file_path": "test.py", "limit": 100}
    )
    formatter = ClaudeCodeFormatter()
    result = formatter._format_tool_use(tool)
    assert result == '● Read(file_path: "test.py", limit: 100)'

def test_tool_result_truncation():
    """Test long tool results are truncated with ctrl+o indicator."""
    # ... implementation
```

**Acceptance Criteria**:
- All tests pass
- Coverage >80% for rendering module
- Edge cases covered (empty content, None values, etc.)

---

#### Task 5.2: Write documentation
- [ ] Add docstrings to all public classes/methods
- [ ] Create `docs/rendering.md` usage guide
- [ ] Update main README with rendering section
- [ ] Add code examples to docstrings

**Documentation Sections**:
1. Quick Start
2. Architecture Overview
3. Configuration Options
4. Custom Formatters (how to extend)
5. Custom Handlers (how to extend)
6. Examples
7. API Reference

**Acceptance Criteria**:
- All public APIs documented
- Usage guide complete with examples
- README updated

---

#### Task 5.3: Integration test with real SDK
- [ ] Test with actual ClaudeSDKClient
- [ ] Test with various message types from real responses
- [ ] Verify UTF-8 characters render correctly in different terminals
- [ ] Test file handler with real conversation

**Acceptance Criteria**:
- Works with real SDK responses
- UTF-8 renders correctly (Windows, Mac, Linux)
- No regressions in existing SDK functionality

---

## Definition of Done (Sprint 1)

- [ ] All tasks completed
- [ ] All tests passing
- [ ] Code coverage >80% for rendering module
- [ ] Documentation complete
- [ ] Examples working
- [ ] No regressions in existing tests
- [ ] UTF-8 rendering matches Claude Code CLI exactly
- [ ] Code reviewed and approved
- [ ] Merged to main branch

---

## Open Questions for This Sprint

1. **MCP Tool Formatting**: Should we detect MCP tools and add "(MCP)" label?
   - **Suggestion**: Yes, detect from server name pattern or metadata

2. **ThinkingBlock Rendering**: How should thinking blocks be displayed?
   - **Suggestion**: Similar to tool use, with truncation

3. **Partial Messages (StreamEvent)**: Should we support incremental rendering?
   - **Suggestion**: Sprint 1 just render final events, defer incremental to Sprint 2

4. **Error Messages**: How to format `is_error=True` tool results?
   - **Suggestion**: Add error indicator, maybe "⎿ ERROR: <content>"

5. **Parameter Truncation**: Long parameter values (100+ chars) - truncate?
   - **Suggestion**: Yes, add max_param_length config option

---

## Estimated Complexity

- **Phase 1 (Abstractions)**: Low - straightforward dataclasses/enums
- **Phase 2 (Base Classes)**: Medium - ABC design requires thought
- **Phase 3 (Implementations)**: High - ClaudeCodeFormatter is complex
- **Phase 4 (Integration)**: Low - mostly wiring
- **Phase 5 (Testing/Docs)**: Medium - comprehensive tests needed

**Total Estimate**: 1-2 focused coding sessions

---

## Success Metrics

After Sprint 1, users should be able to:
1. Import and use renderer with 3 lines of code
2. See Claude Code CLI-style output in their console
3. Log conversations to file automatically
4. Customize output verbosity (MINIMAL, STANDARD, DETAILED)
5. Extend with custom formatters if needed

**User Experience Goal**: "It just works, and looks exactly like Claude Code CLI"
