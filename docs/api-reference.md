# API Reference

Complete reference for the Claude Agent SDK for Python.

## Table of Contents

- [Core Functions](#core-functions)
  - [query()](#query)
- [Client](#client)
  - [ClaudeSDKClient](#claudesdkclient)
- [MCP Tools](#mcp-tools)
  - [tool()](#tool-decorator)
  - [create_sdk_mcp_server()](#create_sdk_mcp_server)
- [Types](#types)
  - [Options](#options)
  - [Messages](#messages)
  - [Hooks](#hooks)
  - [Permissions](#permissions)
  - [MCP Configuration](#mcp-configuration)

---

## Core Functions

### query()

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None
) -> AsyncIterator[Message]
```

**Purpose:** Query Claude Code for one-shot or unidirectional streaming interactions.

**When to use:**
- Simple one-off questions
- Batch processing of independent prompts
- Code generation or analysis tasks
- Automated scripts and CI/CD pipelines
- When you know all inputs upfront

**When NOT to use:**
- Interactive conversations with follow-ups (use `ClaudeSDKClient`)
- When you need to send messages based on responses
- When you need interrupt capabilities
- Long-running sessions with state

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | `str` or `AsyncIterable[dict]` | Yes | The prompt to send to Claude. Can be a simple string or an async iterable for streaming mode. |
| `options` | `ClaudeAgentOptions` or `None` | No | Configuration options. Defaults to `ClaudeAgentOptions()` if None. |
| `transport` | `Transport` or `None` | No | Custom transport implementation. If provided, overrides default transport. |

**Returns:** `AsyncIterator[Message]` - Stream of messages from the conversation.

**Examples:**

**Basic query:**
```python
import anyio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

anyio.run(main)
```

**With options:**
```python
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Create a Python web server",
        options=ClaudeAgentOptions(
            system_prompt="You are an expert Python developer",
            cwd="/home/user/project",
            permission_mode="acceptEdits"
        )
    ):
        print(message)

anyio.run(main)
```

**Streaming mode:**
```python
async def prompts():
    yield {"type": "user", "message": {"role": "user", "content": "Hello"}}
    yield {"type": "user", "message": {"role": "user", "content": "How are you?"}}

async def main():
    async for message in query(prompt=prompts()):
        print(message)

anyio.run(main)
```

---

## Client

### ClaudeSDKClient

```python
class ClaudeSDKClient:
    def __init__(
        self,
        *,
        options: ClaudeAgentOptions | None = None,
        transport: Transport | None = None,
        renderer_config: RendererConfig | None = None
    )
```

**Purpose:** Client for bidirectional, interactive conversations with Claude Code.

**When to use:**
- Building chat interfaces or conversational UIs
- Interactive debugging or exploration sessions
- Multi-turn conversations with context
- When you need to react to Claude's responses
- Real-time applications with user input
- When you need interrupt capabilities

**When NOT to use:**
- Simple one-off questions (use `query()`)
- Batch processing of prompts
- Fire-and-forget automation scripts
- When all inputs are known upfront
- Stateless operations

**Important Caveat:** As of v0.0.20, you cannot use a ClaudeSDKClient instance across different async runtime contexts (e.g., different trio nurseries or asyncio task groups). The client maintains a persistent task group from `connect()` until `disconnect()`.

**Constructor Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `options` | `ClaudeAgentOptions` or `None` | No | Configuration options. Defaults to `ClaudeAgentOptions()`. |
| `transport` | `Transport` or `None` | No | Custom transport implementation. |
| `renderer_config` | `RendererConfig` or `None` | No | Configuration for message rendering (themes, colors, etc.). |

**Methods:**

#### connect()

```python
async def connect(self) -> None
```

Establishes connection to Claude Code. Must be called before sending messages.

**Example:**
```python
client = ClaudeSDKClient()
await client.connect()
```

#### query()

```python
async def query(
    self,
    prompt: str,
    *,
    send_user_message: bool = True
) -> AsyncIterator[Message]
```

Send a query and receive streaming responses.

**Parameters:**
- `prompt` (str): The message to send
- `send_user_message` (bool): Whether to automatically send the prompt as a user message. Default: True.

**Returns:** AsyncIterator of Message objects.

**Example:**
```python
async for message in client.query("What is 2 + 2?"):
    print(message)
```

#### receive_messages()

```python
async def receive_messages(self) -> AsyncIterator[Message]
```

Continuously receive messages from Claude.

**Returns:** AsyncIterator of Message objects.

**Example:**
```python
async for message in client.receive_messages():
    print(message)
```

#### interrupt()

```python
async def interrupt(self) -> None
```

Interrupt the current conversation turn.

**Example:**
```python
await client.interrupt()
```

#### set_permission_mode()

```python
async def set_permission_mode(
    self,
    mode: PermissionMode,
    destination: PermissionUpdateDestination = "memory"
) -> None
```

Update permission mode during conversation.

**Parameters:**
- `mode` (PermissionMode): New permission mode ("default", "acceptEdits", "bypassPermissions")
- `destination` (PermissionUpdateDestination): Where to save ("memory", "project", "global")

**Example:**
```python
await client.set_permission_mode("acceptEdits", destination="project")
```

#### set_model()

```python
async def set_model(
    self,
    model: str,
    destination: PermissionUpdateDestination = "memory"
) -> None
```

Change the Claude model during conversation.

**Parameters:**
- `model` (str): Model identifier (e.g., "claude-sonnet-4-5-20250929")
- `destination` (PermissionUpdateDestination): Where to save the setting

**Example:**
```python
await client.set_model("claude-opus-4-20250514")
```

#### get_server_info()

```python
async def get_server_info(self, server: str) -> dict[str, Any]
```

Get information about an MCP server.

**Parameters:**
- `server` (str): Name of the MCP server

**Returns:** Dictionary with server information.

**Example:**
```python
info = await client.get_server_info("calculator")
print(info)
```

#### disconnect()

```python
async def disconnect(self) -> None
```

Close the connection to Claude Code.

**Example:**
```python
await client.disconnect()
```

#### Context Manager Usage

```python
async with ClaudeSDKClient(options=options) as client:
    async for message in client.query("Hello"):
        print(message)
```

The context manager automatically calls `connect()` on entry and `disconnect()` on exit.

**Complete Example:**

```python
import anyio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant",
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        # First query
        async for message in client.query("Hello, Claude!"):
            print(message)

        # Follow-up based on response
        async for message in client.query("Tell me more about Python"):
            print(message)

        # Interrupt if needed
        await client.interrupt()

anyio.run(main)
```

---

## MCP Tools

The SDK supports creating in-process MCP (Model Context Protocol) servers that run directly in your Python application.

### tool()

```python
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any]
) -> Callable[[Callable], SdkMcpTool]
```

**Purpose:** Decorator for defining MCP tools with type safety.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique identifier for the tool. Used by Claude to reference the tool. |
| `description` | `str` | Human-readable description. Helps Claude understand when to use the tool. |
| `input_schema` | `type` or `dict` | Schema defining input parameters. Can be a dict, TypedDict, or JSON Schema. |

**Returns:** Decorator function that returns an `SdkMcpTool` instance.

**Tool Function Requirements:**
- Must be async (defined with `async def`)
- Receives a single dict argument with input parameters
- Should return a dict with "content" key containing the response
- Can indicate errors with `"is_error": True` in response

**Examples:**

**Basic tool:**
```python
from claude_agent_sdk import tool

@tool("greet", "Greet a user", {"name": str})
async def greet(args):
    return {
        "content": [{
            "type": "text",
            "text": f"Hello, {args['name']}!"
        }]
    }
```

**Multiple parameters:**
```python
@tool("add", "Add two numbers", {"a": float, "b": float})
async def add_numbers(args):
    result = args["a"] + args["b"]
    return {
        "content": [{
            "type": "text",
            "text": f"Result: {result}"
        }]
    }
```

**With error handling:**
```python
@tool("divide", "Divide two numbers", {"a": float, "b": float})
async def divide(args):
    if args["b"] == 0:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Division by zero"
            }],
            "is_error": True
        }

    result = args["a"] / args["b"]
    return {
        "content": [{
            "type": "text",
            "text": f"Result: {result}"
        }]
    }
```

### create_sdk_mcp_server()

```python
def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: list[SdkMcpTool[Any]] | None = None
) -> McpSdkServerConfig
```

**Purpose:** Create an in-process MCP server that runs within your Python application.

**Benefits over external MCP servers:**
- Better performance (no IPC overhead)
- Simpler deployment (single process)
- Easier debugging (same process)
- Direct access to your application's state

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | `str` | Yes | - | Unique identifier for the server |
| `version` | `str` | No | "1.0.0" | Server version string |
| `tools` | `list[SdkMcpTool]` or `None` | No | `None` | List of tools created with @tool decorator |

**Returns:** `McpSdkServerConfig` - Configuration object for `ClaudeAgentOptions.mcp_servers`

**Examples:**

**Simple calculator server:**
```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, query

@tool("add", "Add numbers", {"a": float, "b": float})
async def add(args):
    return {
        "content": [{
            "type": "text",
            "text": f"Sum: {args['a'] + args['b']}"
        }]
    }

@tool("multiply", "Multiply numbers", {"a": float, "b": float})
async def multiply(args):
    return {
        "content": [{
            "type": "text",
            "text": f"Product: {args['a'] * args['b']}"
        }]
    }

calculator = create_sdk_mcp_server(
    name="calculator",
    version="2.0.0",
    tools=[add, multiply]
)

# Use with Claude
options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["add", "multiply"]
)

async for message in query(prompt="What is 5 + 3?", options=options):
    print(message)
```

**Server with application state access:**
```python
class DataStore:
    def __init__(self):
        self.items = []

store = DataStore()

@tool("add_item", "Add item to store", {"item": str})
async def add_item(args):
    store.items.append(args["item"])
    return {
        "content": [{
            "type": "text",
            "text": f"Added: {args['item']}"
        }]
    }

@tool("list_items", "List all items", {})
async def list_items(args):
    items_str = ", ".join(store.items) if store.items else "No items"
    return {
        "content": [{
            "type": "text",
            "text": f"Items: {items_str}"
        }]
    }

server = create_sdk_mcp_server(
    name="store",
    tools=[add_item, list_items]
)
```

---

## Types

### Options

#### ClaudeAgentOptions

```python
@dataclass
class ClaudeAgentOptions:
    """Configuration options for Claude Agent SDK."""

    # Authentication
    # (auto-configured via environment)

    # Model settings
    model: str | None = None  # e.g., "claude-sonnet-4-5-20250929"
    max_budget_usd: float | None = None  # Cost limit in USD

    # Working directory
    cwd: str | None = None  # Defaults to current directory

    # System behavior
    system_prompt: str | SystemPromptPreset | None = None
    system_prompt_source: SettingSource = "memory"

    # Permissions
    permission_mode: PermissionMode = "default"
    permission_mode_source: SettingSource = "memory"
    can_use_tool: CanUseTool | None = None  # Callback for tool permissions

    # Tools
    allowed_tools: list[str] | None = None  # Whitelist of tool names
    blocked_tools: list[str] | None = None  # Blacklist of tool names

    # MCP Servers
    mcp_servers: dict[str, McpServerConfig] | None = None

    # Plugins
    plugins: list[SdkPluginConfig] | None = None

    # Hooks
    hooks: list[tuple[HookMatcher, HookCallback]] | None = None

    # Agent configuration
    agents: dict[str, AgentDefinition] | None = None

    # Output control
    include_partial_messages: bool = False  # Stream partial assistant messages
```

**Key Options Explained:**

**Permission Modes:**
- `"default"`: CLI prompts for dangerous tools
- `"acceptEdits"`: Auto-accept file edits
- `"bypassPermissions"`: Allow all tools (use with caution)

**System Prompt Presets:**
- `"expert-coding-agent"`: Default coding assistant
- `"general-assistant"`: General-purpose assistant
- Custom string for specific behavior

**Setting Sources:**
- `"memory"`: Session-only (not persisted)
- `"project"`: Save to project config
- `"global"`: Save to global config

**Example:**
```python
options = ClaudeAgentOptions(
    model="claude-sonnet-4-5-20250929",
    max_budget_usd=5.0,
    cwd="/home/user/project",
    system_prompt="You are an expert Python developer",
    permission_mode="acceptEdits",
    allowed_tools=["read_file", "write_file"],
    include_partial_messages=True
)
```

### Messages

#### Message Types

```python
Message = UserMessage | AssistantMessage | SystemMessage | ResultMessage
```

**UserMessage:**
```python
@dataclass
class UserMessage:
    type: Literal["user"] = "user"
    message: dict[str, Any]  # {"role": "user", "content": "..."}
    parent_tool_use_id: str | None = None
    session_id: str | None = None
```

**AssistantMessage:**
```python
@dataclass
class AssistantMessage:
    type: Literal["assistant"] = "assistant"
    message: dict[str, Any]  # {"role": "assistant", "content": [...]}
    turn_index: int
    session_id: str
```

**ResultMessage:**
```python
@dataclass
class ResultMessage:
    type: Literal["result"] = "result"
    message: dict[str, Any]
    session_id: str
```

#### Content Blocks

```python
ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock
```

**TextBlock:**
```python
@dataclass
class TextBlock:
    type: Literal["text"] = "text"
    text: str
```

**ToolUseBlock:**
```python
@dataclass
class ToolUseBlock:
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict[str, Any]
```

**ToolResultBlock:**
```python
@dataclass
class ToolResultBlock:
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: list[ContentBlock]
    is_error: bool = False
```

### Hooks

Hooks allow you to intercept and modify SDK behavior at specific lifecycle events.

#### Hook Events

```python
HookEvent = Literal[
    "pre_tool_use",           # Before a tool is executed
    "post_tool_use",          # After a tool completes
    "user_prompt_submit",     # When user submits a message
    "session_start",          # When session begins
    "stop",                   # When session ends
    "subagent_stop",          # When subagent ends
    "pre_compact"             # Before message compaction
]
```

#### HookCallback

```python
HookCallback = Callable[[HookInput], Awaitable[HookJSONOutput | None]]
```

#### Hook Input Types

**PreToolUseHookInput:**
```python
@dataclass
class PreToolUseHookInput(BaseHookInput):
    event: Literal["pre_tool_use"]
    tool_name: str
    tool_input: dict[str, Any]
    context: HookContext
```

**PostToolUseHookInput:**
```python
@dataclass
class PostToolUseHookInput(BaseHookInput):
    event: Literal["post_tool_use"]
    tool_name: str
    tool_input: dict[str, Any]
    tool_output: dict[str, Any]
    context: HookContext
```

#### Hook Output

```python
@dataclass
class AsyncHookJSONOutput:
    """For async hooks that don't block execution."""
    mode: Literal["async"] = "async"

@dataclass
class SyncHookJSONOutput:
    """For sync hooks that can modify behavior."""
    mode: Literal["sync"] = "sync"
    specific_output: HookSpecificOutput
```

#### Example Hooks

**Logging hook:**
```python
from claude_agent_sdk import ClaudeAgentOptions

async def log_tool_use(hook_input):
    if hook_input.event == "pre_tool_use":
        print(f"About to use tool: {hook_input.tool_name}")
        print(f"With input: {hook_input.tool_input}")
    return {"mode": "async"}

options = ClaudeAgentOptions(
    hooks=[
        ({"event": "pre_tool_use"}, log_tool_use)
    ]
)
```

**Permission override hook:**
```python
async def custom_permission(hook_input):
    if hook_input.event == "pre_tool_use":
        if hook_input.tool_name == "dangerous_tool":
            # Deny the tool
            return {
                "mode": "sync",
                "specific_output": {
                    "event": "pre_tool_use",
                    "permission_result": {
                        "type": "deny",
                        "reason": "This tool is not allowed"
                    }
                }
            }
    return None  # Allow by default

options = ClaudeAgentOptions(
    hooks=[
        ({"event": "pre_tool_use"}, custom_permission)
    ]
)
```

### Permissions

#### PermissionMode

```python
PermissionMode = Literal["default", "acceptEdits", "bypassPermissions"]
```

#### PermissionResult

```python
PermissionResult = PermissionResultAllow | PermissionResultDeny

@dataclass
class PermissionResultAllow:
    type: Literal["allow"] = "allow"
    updates: list[PermissionUpdate] | None = None

@dataclass
class PermissionResultDeny:
    type: Literal["deny"] = "deny"
    reason: str
    updates: list[PermissionUpdate] | None = None
```

#### CanUseTool Callback

```python
CanUseTool = Callable[[ToolPermissionContext], Awaitable[PermissionResult]]
```

**Example:**
```python
async def can_use_tool(context: ToolPermissionContext) -> PermissionResult:
    if context.tool_name == "read_file":
        if "/secrets/" in context.tool_input.get("path", ""):
            return PermissionResultDeny(
                reason="Cannot read files in /secrets/ directory"
            )
    return PermissionResultAllow()

options = ClaudeAgentOptions(
    can_use_tool=can_use_tool
)
```

### MCP Configuration

#### McpServerConfig

```python
McpServerConfig = (
    McpStdioServerConfig |
    McpSSEServerConfig |
    McpHttpServerConfig |
    McpSdkServerConfig
)
```

**McpStdioServerConfig (External process):**
```python
@dataclass
class McpStdioServerConfig:
    transport_type: Literal["stdio"]
    command: str  # Command to launch server
    args: list[str] | None = None
    env: dict[str, str] | None = None
```

**McpSdkServerConfig (In-process):**
```python
@dataclass
class McpSdkServerConfig:
    transport_type: Literal["sdk"]
    server: Any  # MCP server instance
```

**Example:**
```python
from claude_agent_sdk import create_sdk_mcp_server, ClaudeAgentOptions

# In-process server
calculator = create_sdk_mcp_server("calc", tools=[...])

# External server
filesystem = {
    "transport_type": "stdio",
    "command": "node",
    "args": ["path/to/server.js"]
}

options = ClaudeAgentOptions(
    mcp_servers={
        "calc": calculator,
        "fs": filesystem
    }
)
```

---

## Rendering Configuration

### RendererConfig

The SDK supports rich theming and styling for message output.

```python
@dataclass
class RendererConfig:
    """Configuration for message rendering."""
    theme: str | dict[str, Any] | None = None
    no_color: bool = False
    force_color: bool = False
```

**Built-in Themes:**
- `"claude-code-default"`: Official Claude Code theme
- `"monokai"`: Monokai color scheme
- `"solarized-dark"`: Solarized dark theme
- `"solarized-light"`: Solarized light theme
- `"github-dark"`: GitHub dark theme
- `"dracula"`: Dracula theme
- `"nord"`: Nord theme
- `"one-dark"`: Atom One Dark theme

**Example:**
```python
from claude_agent_sdk import ClaudeSDKClient, RendererConfig

client = ClaudeSDKClient(
    renderer_config=RendererConfig(
        theme="monokai",
        force_color=True
    )
)
```

**Custom Theme:**
```python
custom_theme = {
    "name": "my-theme",
    "colors": {
        "user": "#00ff00",
        "assistant": "#0000ff",
        "system": "#ff0000"
    }
}

client = ClaudeSDKClient(
    renderer_config=RendererConfig(theme=custom_theme)
)
```

See [docs/rendering.md](rendering.md) for detailed theming documentation.

---

## Error Handling

The SDK uses standard Python exceptions. Always wrap SDK calls in try-except blocks for production use.

**Common patterns:**

```python
import anyio
from claude_agent_sdk import query, ClaudeSDKClient

# With query()
async def safe_query():
    try:
        async for message in query(prompt="Hello"):
            print(message)
    except Exception as e:
        print(f"Query failed: {e}")

# With ClaudeSDKClient
async def safe_client():
    client = ClaudeSDKClient()
    try:
        await client.connect()
        async for message in client.query("Hello"):
            print(message)
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        await client.disconnect()

anyio.run(safe_query)
```

---

## See Also

- [Claude Agent SDK Documentation](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-python)
- [Examples](../examples/)
- [Rendering & Themes](rendering.md)
- [GitHub Repository](https://github.com/anthropics/claude-agent-sdk-python)
