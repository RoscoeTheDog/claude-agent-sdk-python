# Message Rendering System

The Claude Agent SDK includes a flexible message rendering system that formats and displays SDK messages in various styles and destinations. The system is designed with a pluggable architecture similar to Python's logging module, allowing you to easily customize how messages are formatted and where they are displayed.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Configuration Options](#configuration-options)
- [Using Handlers](#using-handlers)
- [Custom Formatters](#custom-formatters)
- [Custom Handlers](#custom-handlers)
- [Examples](#examples)
- [API Reference](#api-reference)

## Quick Start

The simplest way to use the rendering system is with the `display_message()` convenience function:

```python
from claude_agent_sdk.rendering import display_message, RenderLevel

# Simple usage - renders to stdout with default settings
display_message(message)

# Customize the render level
display_message(message, level=RenderLevel.DETAILED)
```

For more control, create a `MessageRenderer` with custom handlers:

```python
from claude_agent_sdk.rendering import (
    MessageRenderer,
    ClaudeCodeFormatter,
    StreamHandler,
    FileHandler,
    RendererConfig,
    RenderLevel,
)

# Create configuration
config = RendererConfig(render_level=RenderLevel.DETAILED)

# Create formatter
formatter = ClaudeCodeFormatter(config)

# Create renderer with multiple handlers
renderer = MessageRenderer()
renderer.add_handler(StreamHandler(formatter))  # Console output
renderer.add_handler(FileHandler(formatter, "session.log"))  # File output

# Render messages
renderer.render(message)
```

## Architecture Overview

The rendering system uses a three-layer architecture:

```
MessageRenderer
├── Handler (WHERE: console, file, custom)
│   ├── StreamHandler (stdout/stderr)
│   ├── FileHandler (file path)
│   └── NullHandler (no-op)
└── Formatter (HOW: format style)
    └── ClaudeCodeFormatter (UTF-8, Claude CLI conventions)
```

### Components

1. **MessageRenderer**: The main coordinator that manages multiple handlers and dispatches messages to them.

2. **Handler**: Controls WHERE messages are sent (stdout, file, network, etc.) and applies filtering logic.

3. **Formatter**: Controls HOW messages are formatted (UTF-8 text, JSON, HTML, etc.).

This separation allows you to:
- Send the same message to multiple destinations simultaneously
- Use different formats for different destinations (e.g., pretty console output + JSON file)
- Filter messages differently for each destination

## Configuration Options

The `RendererConfig` class controls all aspects of rendering:

```python
from claude_agent_sdk.rendering import RendererConfig, RenderLevel

config = RendererConfig(
    # Filtering
    render_level=RenderLevel.STANDARD,  # MINIMAL, STANDARD, DETAILED, DEBUG, ALL
    include_message_types=["UserMessage", "AssistantMessage"],  # Whitelist (optional)
    exclude_message_types=["SystemMessage"],  # Blacklist (optional)

    # Display settings
    show_metadata=False,  # Show message metadata (future enhancement)
    show_tool_inputs=True,  # Show tool input parameters
    show_tool_outputs=True,  # Show tool output content
    compact_mode=False,  # Compact formatting (future enhancement)

    # Content limits
    max_text_length=10000,  # Max chars for text content before truncation
    max_tool_output_length=5000,  # Max chars for tool output before truncation

    # UTF-8 characters (Claude Code CLI defaults)
    bullet="\u25cf",  # ● bullet point
    tree_connector="\u23bf",  # ⎿ tree connector
    arrow="\u2192",  # → arrow
    ellipsis="\u2026",  # … ellipsis
    list_bullet="\u00b7",  # · list bullet
)
```

### Render Levels

Render levels control the amount of detail displayed:

- **MINIMAL** (0): Only user and assistant text messages
- **STANDARD** (1): + tool names and summaries (default)
- **DETAILED** (2): + tool inputs and outputs
- **DEBUG** (3): + system messages
- **ALL** (4): Everything including stream events

## Using Handlers

### StreamHandler

Writes to stdout, stderr, or any text stream:

```python
from claude_agent_sdk.rendering import StreamHandler, ClaudeCodeFormatter
import sys

formatter = ClaudeCodeFormatter()

# Write to stdout (default)
stdout_handler = StreamHandler(formatter)

# Write to stderr
stderr_handler = StreamHandler(formatter, stream=sys.stderr)

# Auto-flush after each message
live_handler = StreamHandler(formatter, auto_flush=True)
```

### FileHandler

Writes to files with UTF-8 encoding:

```python
from claude_agent_sdk.rendering import FileHandler, ClaudeCodeFormatter
from pathlib import Path

formatter = ClaudeCodeFormatter()

# Append to file (default)
log_handler = FileHandler(formatter, "session.log")

# Overwrite file
new_handler = FileHandler(formatter, "output.txt", mode="w")

# Using Path object with subdirectories (auto-created)
path_handler = FileHandler(formatter, Path("logs/session.log"))
```

### NullHandler

Discards all output (useful for testing):

```python
from claude_agent_sdk.rendering import NullHandler, ClaudeCodeFormatter

formatter = ClaudeCodeFormatter()
null_handler = NullHandler(formatter)  # Silences all output
```

### Multiple Handlers

Send messages to multiple destinations simultaneously:

```python
from claude_agent_sdk.rendering import (
    MessageRenderer,
    ClaudeCodeFormatter,
    StreamHandler,
    FileHandler,
    RendererConfig,
    RenderLevel,
)

# Console: minimal output
console_config = RendererConfig(render_level=RenderLevel.MINIMAL)
console_handler = StreamHandler(ClaudeCodeFormatter(console_config))

# File: detailed output
file_config = RendererConfig(render_level=RenderLevel.DETAILED)
file_handler = FileHandler(ClaudeCodeFormatter(file_config), "debug.log")

# Combine handlers
renderer = MessageRenderer()
renderer.add_handler(console_handler)
renderer.add_handler(file_handler)

# One render() call sends to both
renderer.render(message)
```

## Custom Formatters

Create custom formatters by extending the `Formatter` abstract base class:

```python
from claude_agent_sdk.rendering import Formatter, RendererConfig
from claude_agent_sdk.types import (
    UserMessage,
    AssistantMessage,
    SystemMessage,
    ResultMessage,
    StreamEvent,
)
import json

class JSONFormatter(Formatter):
    """Formats messages as JSON objects."""

    def format_user_message(self, message: UserMessage) -> str:
        return json.dumps({
            "type": "user",
            "content": message.content,
            "timestamp": message.timestamp if hasattr(message, "timestamp") else None,
        }, indent=2)

    def format_assistant_message(self, message: AssistantMessage) -> str:
        return json.dumps({
            "type": "assistant",
            "content": [block.model_dump() for block in message.content],
        }, indent=2)

    def format_system_message(self, message: SystemMessage) -> str:
        return json.dumps({
            "type": "system",
            "subtype": message.subtype,
        }, indent=2)

    def format_result_message(self, message: ResultMessage) -> str:
        return json.dumps({
            "type": "result",
            "cost": message.total_cost_usd,
        }, indent=2)

    def format_stream_event(self, message: StreamEvent) -> str:
        return json.dumps({
            "type": "stream",
            "event": message.event,
        }, indent=2)

# Use the custom formatter
formatter = JSONFormatter()
handler = StreamHandler(formatter)
renderer = MessageRenderer()
renderer.add_handler(handler)
```

### Formatter Helpers

The base `Formatter` class provides helper methods:

```python
class MyFormatter(Formatter):
    def format_user_message(self, message: UserMessage) -> str:
        # Truncate long text with indicator
        text = self._truncate_text(
            message.content,
            max_length=500,
            indicator="... +{n} lines (press enter to expand)"
        )

        # Indent lines
        indented = self._indent_lines(text, indent="  ")

        return f"USER:\n{indented}"
```

## Custom Handlers

Create custom handlers by extending the `Handler` abstract base class:

```python
from claude_agent_sdk.rendering import Handler, Formatter
from claude_agent_sdk.types import Message
import requests

class WebhookHandler(Handler):
    """Sends formatted messages to a webhook URL."""

    def __init__(self, formatter: Formatter, webhook_url: str):
        super().__init__(formatter)
        self.webhook_url = webhook_url

    def emit(self, formatted_output: str, message: Message) -> None:
        """Send formatted message to webhook."""
        try:
            response = requests.post(
                self.webhook_url,
                json={
                    "message": formatted_output,
                    "message_type": type(message).__name__,
                },
                timeout=5,
            )
            response.raise_for_status()
        except Exception as e:
            # Log error but don't crash
            print(f"Webhook error: {e}")

# Use the custom handler
formatter = ClaudeCodeFormatter()
webhook_handler = WebhookHandler(formatter, "https://example.com/webhook")
renderer = MessageRenderer()
renderer.add_handler(webhook_handler)
```

### Handler Filtering

Handlers automatically filter messages based on configuration:

```python
from claude_agent_sdk.rendering import Handler, RendererConfig, RenderLevel

# Create config that excludes SystemMessage
config = RendererConfig(
    exclude_message_types=["SystemMessage"],
    render_level=RenderLevel.STANDARD,
)

# Handler will automatically skip SystemMessage
handler = StreamHandler(ClaudeCodeFormatter(config))

# Or override should_render() for custom filtering
class FilteredHandler(Handler):
    def should_render(self, message: Message) -> bool:
        # Custom filtering logic
        if isinstance(message, UserMessage):
            # Only render user messages containing "important"
            return "important" in str(message.content).lower()
        return super().should_render(message)
```

## Examples

### Example 1: Console-Only with Different Levels

```python
from claude_agent_sdk.rendering import display_message, RenderLevel

# Minimal: only user/assistant text
display_message(message, level=RenderLevel.MINIMAL)

# Standard: + tool names and summaries (default)
display_message(message, level=RenderLevel.STANDARD)

# Detailed: + tool inputs/outputs
display_message(message, level=RenderLevel.DETAILED)

# Debug: + system messages
display_message(message, level=RenderLevel.DEBUG)

# All: everything including stream events
display_message(message, level=RenderLevel.ALL)
```

### Example 2: Console + File with Different Configs

```python
from claude_agent_sdk.rendering import (
    MessageRenderer,
    ClaudeCodeFormatter,
    StreamHandler,
    FileHandler,
    RendererConfig,
    RenderLevel,
)

# Console: minimal, no tool details
console_config = RendererConfig(
    render_level=RenderLevel.MINIMAL,
    show_tool_inputs=False,
    show_tool_outputs=False,
)
console_handler = StreamHandler(ClaudeCodeFormatter(console_config))

# File: detailed with everything
file_config = RendererConfig(
    render_level=RenderLevel.DEBUG,
    show_tool_inputs=True,
    show_tool_outputs=True,
    max_tool_output_length=50000,  # Higher limit for files
)
file_handler = FileHandler(ClaudeCodeFormatter(file_config), "full_session.log")

# Combine
renderer = MessageRenderer()
renderer.add_handler(console_handler)
renderer.add_handler(file_handler)

# Use with SDK
from claude_agent_sdk import ClaudeSDKClient

client = ClaudeSDKClient(api_key="your-api-key")

for message in client.query("Explain quantum computing"):
    renderer.render(message)
```

### Example 3: Custom Filtering by Message Type

```python
from claude_agent_sdk.rendering import (
    MessageRenderer,
    ClaudeCodeFormatter,
    FileHandler,
    RendererConfig,
)

# Only render AssistantMessage to one file
assistant_config = RendererConfig(
    include_message_types=["AssistantMessage"],
)
assistant_handler = FileHandler(
    ClaudeCodeFormatter(assistant_config),
    "assistant_only.log"
)

# Only render ToolUseBlock and ToolResultBlock to another
tool_config = RendererConfig(
    include_message_types=["AssistantMessage"],  # Tools are in AssistantMessage
    show_tool_inputs=True,
    show_tool_outputs=True,
)
tool_handler = FileHandler(
    ClaudeCodeFormatter(tool_config),
    "tools.log"
)

renderer = MessageRenderer()
renderer.add_handler(assistant_handler)
renderer.add_handler(tool_handler)
```

### Example 4: Live Streaming with Auto-Flush

```python
from claude_agent_sdk.rendering import (
    MessageRenderer,
    ClaudeCodeFormatter,
    StreamHandler,
    RendererConfig,
    RenderLevel,
)
from claude_agent_sdk import ClaudeSDKClient

# Configure for live output
config = RendererConfig(render_level=RenderLevel.STANDARD)
formatter = ClaudeCodeFormatter(config)

# Auto-flush ensures immediate output
handler = StreamHandler(formatter, auto_flush=True)

renderer = MessageRenderer()
renderer.add_handler(handler)

# Stream responses
client = ClaudeSDKClient(api_key="your-api-key")

for message in client.stream("Write a poem about coding"):
    renderer.render(message)  # Output appears immediately
```

### Example 5: Migration from Old Pattern

If you were using this pattern before:

```python
# OLD: Manual rendering
for message in client.query("Hello"):
    if isinstance(message, UserMessage):
        print(f"User: {message.content}")
    elif isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
```

Replace with:

```python
# NEW: Use rendering system
from claude_agent_sdk.rendering import display_message

for message in client.query("Hello"):
    display_message(message)
```

## API Reference

### Classes

#### `MessageRenderer`

Main coordinator for rendering messages.

**Methods**:
- `add_handler(handler: Handler)` - Add a handler to the renderer
- `remove_handler(handler: Handler)` - Remove a handler from the renderer
- `clear_handlers()` - Remove all handlers
- `render(message: Message)` - Render a message through all handlers

**Example**:
```python
renderer = MessageRenderer()
renderer.add_handler(console_handler)
renderer.add_handler(file_handler)
renderer.render(message)
```

---

#### `Formatter` (Abstract Base Class)

Base class for formatters.

**Abstract Methods** (must implement):
- `format_user_message(message: UserMessage) -> str`
- `format_assistant_message(message: AssistantMessage) -> str`
- `format_system_message(message: SystemMessage) -> str`
- `format_result_message(message: ResultMessage) -> str`
- `format_stream_event(message: StreamEvent) -> str`

**Helper Methods**:
- `format(message: Message) -> str` - Main entry point, dispatches to type-specific methods
- `_truncate_text(text, max_length, indicator) -> str` - Truncate with indicator
- `_indent_lines(text, indent) -> str` - Indent all lines

---

#### `Handler` (Abstract Base Class)

Base class for handlers.

**Abstract Methods** (must implement):
- `emit(formatted_output: str, message: Message)` - Write output to destination

**Methods**:
- `should_render(message: Message) -> bool` - Filtering logic based on config
- `handle(message: Message)` - Main entry point: filter + format + emit

---

#### `ClaudeCodeFormatter`

Formats messages to match Claude Code CLI UTF-8 rendering.

**Constructor**:
```python
ClaudeCodeFormatter(config: RendererConfig | None = None)
```

**Output Format**:
- User messages: `● User: <text>`
- Assistant text: `● <text>`
- Tool use: `● <tool>(<param>: "value", ...)`
- Tool results: `  ⎿  <output>`
- Result messages: `● Result ended\n  Cost: $<amount>`

---

#### `StreamHandler`

Writes to text streams (stdout/stderr).

**Constructor**:
```python
StreamHandler(
    formatter: Formatter,
    config: RendererConfig | None = None,
    stream: TextIO | None = None,  # Default: sys.stdout
    auto_flush: bool = False,
)
```

---

#### `FileHandler`

Writes to files with UTF-8 encoding.

**Constructor**:
```python
FileHandler(
    formatter: Formatter,
    filepath: str | Path,
    config: RendererConfig | None = None,
    mode: str = "a",  # "a" for append, "w" for overwrite
    encoding: str = "utf-8",
)
```

**Methods**:
- `close()` - Explicitly close file handle

---

#### `NullHandler`

Discards all output (no-op).

**Constructor**:
```python
NullHandler(formatter: Formatter, config: RendererConfig | None = None)
```

---

#### `RenderLevel`

Enum for controlling rendering detail.

**Values**:
- `MINIMAL = 0` - Only user/assistant text
- `STANDARD = 1` - + tool names and summaries (default)
- `DETAILED = 2` - + tool inputs/outputs
- `DEBUG = 3` - + system messages
- `ALL = 4` - Everything including stream events

**Example**:
```python
from claude_agent_sdk.rendering import RenderLevel

if RenderLevel.DETAILED > RenderLevel.STANDARD:
    print("More detailed")
```

---

#### `RendererConfig`

Configuration dataclass for rendering.

**Fields**:

*Filtering*:
- `render_level: RenderLevel = STANDARD` - Detail level
- `include_message_types: list[str] = []` - Whitelist of message types
- `exclude_message_types: list[str] = []` - Blacklist of message types

*Display settings*:
- `show_metadata: bool = False` - Show message metadata (future)
- `show_tool_inputs: bool = True` - Show tool parameters
- `show_tool_outputs: bool = True` - Show tool results
- `compact_mode: bool = False` - Compact formatting (future)

*Content limits*:
- `max_text_length: int = 10000` - Max chars for text before truncation
- `max_tool_output_length: int = 5000` - Max chars for tool output before truncation

*UTF-8 characters*:
- `bullet: str = "●"` - Bullet point character
- `tree_connector: str = "⎿"` - Tree connector character
- `arrow: str = "→"` - Arrow character
- `ellipsis: str = "…"` - Ellipsis character
- `list_bullet: str = "·"` - List bullet character

**Example**:
```python
config = RendererConfig(
    render_level=RenderLevel.DETAILED,
    exclude_message_types=["SystemMessage"],
    max_text_length=5000,
)
```

---

### Functions

#### `display_message()`

Convenience function for quick rendering to stdout.

**Signature**:
```python
def display_message(
    message: Message,
    level: RenderLevel = RenderLevel.STANDARD,
    stream: TextIO | None = None,
) -> None
```

**Parameters**:
- `message` - Message object to render
- `level` - Render level (default: STANDARD)
- `stream` - Output stream (default: stdout)

**Example**:
```python
from claude_agent_sdk.rendering import display_message, RenderLevel

display_message(message)
display_message(message, level=RenderLevel.DETAILED)
```

---

## Thread Safety

The `MessageRenderer` class uses locks to ensure thread-safe handler management. You can safely call `render()` from multiple threads simultaneously.

```python
import threading
from claude_agent_sdk.rendering import MessageRenderer

renderer = MessageRenderer()
# ... add handlers ...

def render_worker(message):
    renderer.render(message)  # Thread-safe

threads = [threading.Thread(target=render_worker, args=(msg,)) for msg in messages]
for t in threads:
    t.start()
```

## Error Handling

If a handler raises an exception during `emit()`, the renderer logs the error to stderr and continues with other handlers:

```python
# If one handler fails, others still receive the message
renderer.add_handler(console_handler)  # Works fine
renderer.add_handler(broken_handler)   # Raises exception
renderer.add_handler(file_handler)     # Still receives message

renderer.render(message)
# Output: "Error in handler BrokenHandler: ..." to stderr
# console_handler and file_handler still work
```

## Performance Considerations

- **Truncation**: Configure `max_text_length` and `max_tool_output_length` to avoid rendering extremely large outputs
- **File Buffering**: FileHandler flushes after each message for reliability. For high-throughput scenarios, consider buffering
- **Stream Flushing**: Use `auto_flush=True` only when needed (live output), as it has performance overhead
- **Filtering**: Use `include_message_types` and `exclude_message_types` to avoid formatting messages you don't need

## Future Enhancements (Sprint 2+)

The following features are planned for future releases:

- **Rich formatting**: Colors, bold/italic, syntax highlighting
- **Metadata display**: Timestamps, message IDs, token counts
- **Interactive features**: Expandable sections, clickable links
- **Stream events**: Incremental updates for streaming responses
- **Compact mode**: Denser output format
- **HTML/Markdown formatters**: Additional output formats
- **Async handlers**: Non-blocking I/O for high-throughput scenarios
