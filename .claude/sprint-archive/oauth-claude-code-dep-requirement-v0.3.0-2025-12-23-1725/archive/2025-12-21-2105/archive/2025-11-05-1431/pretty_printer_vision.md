# Claude Code CLI Pretty Printer - Vision & Design

**Created**: 2025-11-05
**Status**: Planning
**Owner**: claude-agent-sdk-python

## Executive Summary

Create a pluggable, configurable pretty printer system that emulates Claude Code CLI rendering for SDK message output. The system will support multiple output handlers (console, file, custom) with progressive enhancement from baseline ASCII rendering to rich formatting with colors, metadata, and interactive features.

---

## Background & Motivation

### Current State
The SDK currently provides raw message objects (UserMessage, AssistantMessage, ToolUseBlock, etc.) with no built-in rendering. Users must manually extract and format content for display, as seen in examples/streaming_mode.py.

### Goals
1. **Parity with Claude Code CLI**: Match the console rendering behavior users see when running `claude` directly
2. **Pluggable Architecture**: Swap renderers via configuration (similar to Python logging handlers)
3. **Progressive Enhancement**: Start with ASCII baseline, add styling/metadata incrementally
4. **Developer Experience**: Simple defaults for quick starts, deep customization for power users

---

## Architecture Design

### Core Components

```
claude_agent_sdk/
├── rendering/
│   ├── __init__.py              # Public API exports
│   ├── base.py                  # MessageRenderer ABC + Handler ABC
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── stream_handler.py   # Console/stdout handler
│   │   ├── file_handler.py     # File output handler
│   │   └── null_handler.py     # Silent/no-op handler
│   ├── formatters/
│   │   ├── __init__.py
│   │   ├── base_formatter.py   # Plain ASCII formatter (baseline)
│   │   ├── rich_formatter.py   # Rich console with colors (future)
│   │   └── markdown_formatter.py # Markdown output (future)
│   └── config.py                # Configuration classes
```

### Key Abstractions

#### 1. MessageRenderer (Main Entry Point)
```python
class MessageRenderer:
    """
    Main rendering coordinator. Dispatches messages to handlers.

    Usage:
        renderer = MessageRenderer()
        renderer.add_handler(StreamHandler(formatter=BaseFormatter()))

        async for msg in client.receive_messages():
            renderer.render(msg)
    """
    def __init__(self, handlers: list[Handler] = None)
    def add_handler(self, handler: Handler) -> None
    def remove_handler(self, handler: Handler) -> None
    def render(self, message: Message) -> None
```

#### 2. Handler (Output Destination)
```python
class Handler(ABC):
    """
    Abstract handler - defines WHERE output goes.
    Similar to logging.Handler pattern.
    """
    def __init__(self, formatter: Formatter, level: RenderLevel = RenderLevel.ALL)

    @abstractmethod
    def emit(self, formatted_output: str, message: Message) -> None
        """Write formatted output to destination"""

    def should_render(self, message: Message) -> bool
        """Filter messages by type/level"""
```

**Concrete Handlers**:
- `StreamHandler(stream=sys.stdout)`: Console output
- `FileHandler(filepath, mode='a')`: File output
- `NullHandler()`: No-op for testing/silence

#### 3. Formatter (Content Formatting)
```python
class Formatter(ABC):
    """
    Abstract formatter - defines HOW messages are formatted.
    """
    @abstractmethod
    def format_user_message(self, msg: UserMessage) -> str

    @abstractmethod
    def format_assistant_message(self, msg: AssistantMessage) -> str

    @abstractmethod
    def format_tool_use(self, block: ToolUseBlock) -> str

    @abstractmethod
    def format_tool_result(self, block: ToolResultBlock) -> str

    @abstractmethod
    def format_system_message(self, msg: SystemMessage) -> str

    @abstractmethod
    def format_result_message(self, msg: ResultMessage) -> str

    @abstractmethod
    def format_stream_event(self, msg: StreamEvent) -> str
```

**Concrete Formatters**:
- `BaseFormatter`: Plain ASCII, baseline Claude Code CLI rendering
- `RichFormatter` (Sprint 2+): Colors, styling, rich console features
- `MarkdownFormatter` (Sprint 3+): Markdown-formatted output

#### 4. RenderLevel (Message Filtering)
```python
class RenderLevel(Enum):
    """
    Control verbosity of output.
    """
    MINIMAL = 0      # Only user/assistant text content
    STANDARD = 1     # + tool names, result summaries
    DETAILED = 2     # + tool inputs/outputs, metadata
    DEBUG = 3        # + system messages, stream events
    ALL = 4          # Everything
```

#### 5. RendererConfig (Configuration)
```python
@dataclass
class RendererConfig:
    """
    Configuration for rendering behavior.
    """
    # Display settings
    show_metadata: bool = False          # Show message IDs, timestamps
    show_tool_inputs: bool = False       # Show full tool input JSON
    show_tool_outputs: bool = True       # Show tool results
    compact_mode: bool = False           # Minimize whitespace

    # Content limits
    max_text_length: int | None = None   # Truncate long text blocks
    max_tool_output_length: int = 500    # Truncate tool results

    # Filtering
    render_level: RenderLevel = RenderLevel.STANDARD
    include_message_types: list[type] | None = None
    exclude_message_types: list[type] | None = None
```

---

## Claude Code CLI Rendering Conventions (Baseline)

Based on actual Claude Code CLI output, here are the rendering conventions:

### User Messages (Simple)
```
● User: <message content>
```

### User Messages (With Answers to Questions)
```
● User answered Claude's questions:
  ⎿  · <question text> → <answer text>
     · <question text> → <answer text>
```

### Assistant Messages (Text)
```
● <assistant message text>
```

### Assistant Messages (Tool Calls)
```
● <optional context message>

● <tool-name> - <function-name> (MCP)(<param1>: "<value1>", <param2>: <value2>)
  ⎿  <result preview line 1>
     <result preview line 2>
     … +N lines (ctrl+o to expand)
```

**Example from actual output**:
```
● context7-local - resolve-library-id (MCP)(libraryName: "claude-code")
  ⎿  Available Libraries (top matches):

     Each result includes:
     … +222 lines (ctrl+o to expand)
```

### Tool Use Patterns
- **Tool call header**: `● <server>-<tool> (MCP)(<params>)` or `● <tool>(<params>)`
- **Result nesting**: `⎿` for first result line, then indented continuation
- **Truncation**: `… +N lines (ctrl+o to expand)` for long outputs
- **Parameter format**: `(key: "value", key2: value2)` - strings quoted, others not

### System Messages
- Not displayed in normal operation
- Debug mode may show with `●` prefix

### Result Messages
```
● Result ended
  Cost: $<total_cost_usd>
```

### Stream Events
- Not typically rendered in CLI (internal streaming mechanics)
- May be rendered in verbose/debug mode with `●` prefix

### Hierarchical Structure
```
● Top-level item (user/assistant/tool)
  ⎿  Nested content (results, details)
     Continuation lines (same indent as ⎿ content)
     … +N lines (ctrl+o to expand)
```

### Character Usage Guide
- `●` - Main item bullet (user messages, assistant text, tool calls)
- `⎿` - Tree connector (result/output indicator)
- `→` - Arrow (user selections, mappings)
- `…` - Ellipsis (content truncation)
- `·` - Middle dot (list items within nested content)

---

## Sprint Plan

### Sprint 1: Core Infrastructure (Baseline Rendering)
**Goal**: Working system with ASCII-only Claude Code CLI-style rendering

**Deliverables**:
1. Base abstractions (`MessageRenderer`, `Handler`, `Formatter`)
2. `StreamHandler` (stdout/stderr output)
3. `FileHandler` (file output)
4. `BaseFormatter` (plain ASCII, Claude Code CLI conventions)
5. `RendererConfig` (configuration system)
6. Integration example with ClaudeSDKClient
7. Unit tests for core components
8. Basic documentation

**Success Criteria**:
- Can render all message types to console in Claude Code CLI format
- Can configure output destination (console vs file)
- Can filter messages by type/level
- Zero external dependencies beyond stdlib
- All existing tests pass

### Sprint 2: Rich Formatting & Metadata
**Goal**: Enhanced visual output with colors, styling, metadata

**Deliverables**:
1. `RichFormatter` using rich console library
2. Color coding (user=blue, assistant=green, tools=yellow, errors=red)
3. Metadata display (timestamps, message IDs, session IDs)
4. Tool input/output expansion/collapse
5. Progress indicators for long operations
6. Interactive features (if terminal supports)

**Dependencies**: `rich` library

### Sprint 3: Advanced Features
**Goal**: Production-ready features for diverse use cases

**Deliverables**:
1. `MarkdownFormatter` for markdown output
2. `JSONFormatter` for structured logs
3. Template-based custom formatting
4. Async handler support (non-blocking I/O)
5. Log rotation for file handlers
6. Performance optimizations
7. Comprehensive documentation + cookbook

---

## API Usage Examples

### Quick Start (Default Console Output)
```python
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.rendering import MessageRenderer, StreamHandler, BaseFormatter

async with ClaudeSDKClient() as client:
    # Setup renderer with console output
    renderer = MessageRenderer()
    renderer.add_handler(StreamHandler(formatter=BaseFormatter()))

    await client.query("What is 2+2?")

    async for msg in client.receive_response():
        renderer.render(msg)
```

### Multi-Handler Configuration
```python
from claude_agent_sdk.rendering import (
    MessageRenderer, StreamHandler, FileHandler,
    BaseFormatter, RendererConfig, RenderLevel
)

# Console: minimal output
console_handler = StreamHandler(
    formatter=BaseFormatter(config=RendererConfig(
        render_level=RenderLevel.MINIMAL,
        compact_mode=True
    ))
)

# File: detailed logging
file_handler = FileHandler(
    filepath="conversation.log",
    formatter=BaseFormatter(config=RendererConfig(
        render_level=RenderLevel.DETAILED,
        show_metadata=True,
        show_tool_inputs=True
    ))
)

renderer = MessageRenderer(handlers=[console_handler, file_handler])

async for msg in client.receive_response():
    renderer.render(msg)  # Goes to both console + file
```

### Custom Filtering
```python
from claude_agent_sdk.types import AssistantMessage, UserMessage

config = RendererConfig(
    include_message_types=[UserMessage, AssistantMessage],
    render_level=RenderLevel.STANDARD
)

renderer = MessageRenderer()
renderer.add_handler(StreamHandler(formatter=BaseFormatter(config=config)))
```

### Integration with ClaudeSDKClient (Future)
```python
# Convenience method on client (Sprint 2+)
async with ClaudeSDKClient() as client:
    client.enable_rendering(
        handlers=[StreamHandler()],
        auto_render=True  # Automatically render all messages
    )

    await client.query("Help me debug this code")
    # Messages auto-rendered as they arrive
```

---

## Technical Considerations

### UTF-8 Output with Claude Code CLI Characters (Sprint 1)
- **Rationale**: Match Claude Code CLI's actual rendering format (UTF-8 enhanced)
- **Special Characters Used by Claude Code CLI**:
  - `●` (U+25CF): Bullet points for main items (user messages, assistant actions, tool calls)
  - `⎿` (U+23BF): Tree connector for nested content/results
  - `→` (U+2192): Arrows for user selections, value display
  - `…` (U+2026): Ellipsis for truncation
  - `·` (U+00B7): Middle dot for list items
- **Expandable Content**: `(ctrl+o to expand)` notation for truncated content
- **Encoding**: UTF-8 for all output (matches Claude Code CLI)
- **Fallback**: Detect terminal capabilities, gracefully degrade to ASCII if UTF-8 unsupported

### Thread Safety
- Handlers should be thread-safe (use locks if mutable state)
- Formatters are stateless (safe by design)
- MessageRenderer uses lock for handler list modifications

### Performance
- Lazy formatting (only format if handler will emit)
- Buffered file I/O (FileHandler)
- Avoid blocking on I/O in async contexts (Sprint 3: async handlers)

### Extensibility
- Users can subclass `Handler` and `Formatter` for custom behavior
- Plugin system for formatters (Sprint 3+)
- Configuration via JSON/YAML files (Sprint 3+)

---

## Open Questions

1. **Streaming Support**: Should formatters handle partial messages (StreamEvent)?
   - **Answer (Sprint 1)**: Yes, but basic support only. Rich streaming in Sprint 2.

2. **Error Handling**: How should renderers handle formatting errors?
   - **Answer**: Try-except in render(), log error, emit fallback "Error rendering message"

3. **Backwards Compatibility**: Should we add `display_message()` helper for easy migration from examples?
   - **Answer**: Yes, add in Sprint 1 as convenience function

4. **Configuration File**: Support loading RendererConfig from file?
   - **Answer**: Defer to Sprint 3

5. **MCP Tool Rendering**: Special formatting for MCP tool calls?
   - **Answer**: Treat same as normal tools in Sprint 1, consider special formatting in Sprint 2

---

## Success Metrics

### Sprint 1
- [ ] All message types render correctly
- [ ] Console + file output working
- [ ] Zero regression in existing tests
- [ ] Documentation with 3+ examples
- [ ] Code coverage >80%

### Sprint 2
- [ ] Rich formatting works in 90% of terminals
- [ ] User feedback: "looks professional"
- [ ] Performance: <5ms overhead per message

### Sprint 3
- [ ] 5+ custom formatter examples in docs
- [ ] Production use in 1+ real project
- [ ] API stability (no breaking changes for 6 months)

---

## Migration Path

### Phase 1: Opt-in (Sprint 1)
- New `rendering` module available
- Examples updated to show usage
- No breaking changes to existing code

### Phase 2: Convenience (Sprint 2)
- Add `client.enable_rendering()` helper
- Update quick_start.py to use renderer by default
- Still fully optional

### Phase 3: Default (Sprint 3+)
- Consider making rendering default behavior
- Add `--no-render` flag or `enable_rendering=False` to disable
- Discuss with users first

---

## Related Work

- **Python logging module**: Inspiration for Handler/Formatter pattern
- **Rich library**: Target for Sprint 2 rich formatting
- **Claude Code CLI**: Reference implementation for rendering conventions
- **TypeScript SDK**: Check for similar renderer implementation

---

## Appendix: Message Type Hierarchy

```
Message (Union)
├── UserMessage
│   └── content: str | list[ContentBlock]
├── AssistantMessage
│   └── content: list[ContentBlock]
│       ├── TextBlock
│       ├── ThinkingBlock
│       ├── ToolUseBlock
│       └── ToolResultBlock
├── SystemMessage
│   └── subtype: str, data: dict
├── ResultMessage
│   └── cost, usage, duration, etc.
└── StreamEvent
    └── partial message updates
```

---

**Next Steps**:
1. Get user approval on Sprint 1 plan
2. Create Sprint 1 implementation tasks
3. Begin implementation
