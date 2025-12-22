# Claude Agent SDK for Python

Python SDK for Claude Agent. See the [Claude Agent SDK documentation](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-python) for more information.

## Installation

```bash
pip install claude-agent-sdk
```

**Prerequisites:**
- Python 3.10+
- Node.js
- Claude Code 2.0.0+: `npm install -g @anthropic-ai/claude-code`

## Quick Start

```python
import anyio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

anyio.run(main)
```

## Authentication

The SDK supports two authentication methods:

1. **OAuth (Subscription)** - Use your Claude Max/Pro subscription via OAuth tokens (recommended)
2. **API Key** - Traditional pay-per-token API pricing

### OAuth Authentication (Subscription)

OAuth authentication uses your Claude subscription (Max/Pro) instead of pay-per-token API pricing. The SDK automatically detects and uses OAuth credentials from `~/.claude/.credentials.json`.

**First-time setup:**

```python
from claude_agent_sdk import query

# On first run, SDK will prompt for browser login if needed
async for message in query(prompt="Hello Claude"):
    print(message)
```

The SDK will:
1. Check for valid OAuth credentials
2. If missing/expired, prompt you to login via browser
3. Save credentials to `~/.claude/.credentials.json`
4. Auto-refresh tokens when they expire

**Manual login:**

```bash
claude /login
```

### API Key Authentication

Set your API key via environment variable:

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-...
```

Or programmatically:

```python
import os
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-api03-..."
```

### Authentication Configuration

Control authentication behavior with environment variables or SDK options:

#### Environment Variables

```bash
# Authentication mode (default: "auto")
export CLAUDE_AUTH_MODE=oauth          # Force OAuth only
export CLAUDE_AUTH_MODE=api_key        # Force API key only
export CLAUDE_AUTH_MODE=auto           # Auto-detect (try OAuth first)

# Fallback behavior (default: enabled)
export CLAUDE_AUTH_FALLBACK=true       # Fallback to API key if OAuth fails
export CLAUDE_AUTH_FALLBACK=false      # No fallback, error if OAuth fails

# Strict mode (default: false)
export CLAUDE_AUTH_STRICT=true         # Fail fast with no fallback

# Interactive mode (default: auto-detect)
export CLAUDE_AUTH_INTERACTIVE=false   # Skip browser login (CI/CD)
export CLAUDE_AUTH_INTERACTIVE=true    # Allow browser login
```

#### Programmatic Configuration

```python
from claude_agent_sdk import ClaudeAgentOptions

# Force OAuth with fallback to API key
options = ClaudeAgentOptions(
    auth_mode="oauth",
    auth_fallback=True,
    auth_interactive=True
)

# Strict OAuth only (no fallback, fail if OAuth unavailable)
options = ClaudeAgentOptions(
    auth_mode="oauth",
    auth_fallback=False
)

# CI/CD mode (no browser login, use existing credentials or API key)
options = ClaudeAgentOptions(
    auth_mode="auto",
    auth_interactive=False,
    auth_fallback=True
)

async for message in query(prompt="Hello", options=options):
    print(message)
```

### Authentication Priority

The SDK uses this priority chain:

1. **Environment variables** (highest priority)
   - `CLAUDE_AUTH_MODE`, `CLAUDE_AUTH_FALLBACK`, `CLAUDE_AUTH_STRICT`, `CLAUDE_AUTH_INTERACTIVE`

2. **SDK options** (medium priority)
   - `ClaudeAgentOptions(auth_mode=..., auth_fallback=..., auth_interactive=...)`

3. **Auto-detection** (lowest priority)
   - Try OAuth first, fallback to API key if OAuth unavailable

### Troubleshooting

**"OAuth credentials not found"**
- Run `claude /login` to authenticate
- Or set `ANTHROPIC_API_KEY` to use API key authentication

**"OAuth credentials expired"**
- SDK auto-refreshes tokens automatically
- If refresh fails, SDK will prompt for browser login
- Or run `claude /login` manually

**"Browser login not available in non-interactive mode"**
- Set `CLAUDE_AUTH_INTERACTIVE=false` for CI/CD
- Ensure valid credentials exist before running
- Or use API key authentication: `CLAUDE_AUTH_MODE=api_key`

**Fallback behavior**
- By default, SDK falls back to API key if OAuth fails
- Set `CLAUDE_AUTH_FALLBACK=false` to disable fallback
- Set `CLAUDE_AUTH_STRICT=true` for fail-fast behavior

### Authentication Examples

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Example 1: Auto-detect (default) - Try OAuth, fallback to API key
async for message in query(prompt="Hello"):
    print(message)

# Example 2: Force OAuth only - Fail if OAuth unavailable
options = ClaudeAgentOptions(auth_mode="oauth", auth_fallback=False)
async for message in query(prompt="Hello", options=options):
    print(message)

# Example 3: Force API key only
options = ClaudeAgentOptions(auth_mode="api_key")
async for message in query(prompt="Hello", options=options):
    print(message)

# Example 4: CI/CD mode - No browser login, use existing credentials
options = ClaudeAgentOptions(auth_interactive=False, auth_fallback=True)
async for message in query(prompt="Hello", options=options):
    print(message)

# Example 5: Strict OAuth - Fail fast if OAuth unavailable (no fallback)
options = ClaudeAgentOptions(
    auth_mode="oauth",
    auth_fallback=False,
    auth_interactive=True
)
async for message in query(prompt="Hello", options=options):
    print(message)
```

## Basic Usage: query()

`query()` is an async function for querying Claude Code. It returns an `AsyncIterator` of response messages. See [src/claude_agent_sdk/query.py](src/claude_agent_sdk/query.py).

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

# Simple query
async for message in query(prompt="Hello Claude"):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)

# With options
options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant",
    max_turns=1
)

async for message in query(prompt="Tell me a joke", options=options):
    print(message)
```

### Using Tools

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Bash"],
    permission_mode='acceptEdits'  # auto-accept file edits
)

async for message in query(
    prompt="Create a hello.py file",
    options=options
):
    # Process tool use and results
    pass
```

### Working Directory

```python
from pathlib import Path

options = ClaudeAgentOptions(
    cwd="/path/to/project"  # or Path("/path/to/project")
)
```

## ClaudeSDKClient

`ClaudeSDKClient` supports bidirectional, interactive conversations with Claude
Code. See [src/claude_agent_sdk/client.py](src/claude_agent_sdk/client.py).

Unlike `query()`, `ClaudeSDKClient` additionally enables **custom tools** and **hooks**, both of which can be defined as Python functions.

### Custom Tools (as In-Process SDK MCP Servers)

A **custom tool** is a Python function that you can offer to Claude, for Claude to invoke as needed.

Custom tools are implemented in-process MCP servers that run directly within your Python application, eliminating the need for separate processes that regular MCP servers require.

For an end-to-end example, see [MCP Calculator](examples/mcp_calculator.py).

#### Creating a Simple Tool

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient

# Define a tool using the @tool decorator
@tool("greet", "Greet a user", {"name": str})
async def greet_user(args):
    return {
        "content": [
            {"type": "text", "text": f"Hello, {args['name']}!"}
        ]
    }

# Create an SDK MCP server
server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user]
)

# Use it with Claude
options = ClaudeAgentOptions(
    mcp_servers={"tools": server},
    allowed_tools=["mcp__tools__greet"]
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Greet Alice")

    # Extract and print response
    async for msg in client.receive_response():
        print(msg)
```

#### Benefits Over External MCP Servers

- **No subprocess management** - Runs in the same process as your application
- **Better performance** - No IPC overhead for tool calls
- **Simpler deployment** - Single Python process instead of multiple
- **Easier debugging** - All code runs in the same process
- **Type safety** - Direct Python function calls with type hints

#### Migration from External Servers

```python
# BEFORE: External MCP server (separate process)
options = ClaudeAgentOptions(
    mcp_servers={
        "calculator": {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "calculator_server"]
        }
    }
)

# AFTER: SDK MCP server (in-process)
from my_tools import add, subtract  # Your tool functions

calculator = create_sdk_mcp_server(
    name="calculator",
    tools=[add, subtract]
)

options = ClaudeAgentOptions(
    mcp_servers={"calculator": calculator}
)
```

#### Mixed Server Support

You can use both SDK and external MCP servers together:

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "internal": sdk_server,      # In-process SDK server
        "external": {                # External subprocess server
            "type": "stdio",
            "command": "external-server"
        }
    }
)
```

### Hooks

A **hook** is a Python function that the Claude Code *application* (*not* Claude) invokes at specific points of the Claude agent loop. Hooks can provide deterministic processing and automated feedback for Claude. Read more in [Claude Code Hooks Reference](https://docs.anthropic.com/en/docs/claude-code/hooks).

For more examples, see examples/hooks.py.

#### Example

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, HookMatcher

async def check_bash_command(input_data, tool_use_id, context):
    tool_name = input_data["tool_name"]
    tool_input = input_data["tool_input"]
    if tool_name != "Bash":
        return {}
    command = tool_input.get("command", "")
    block_patterns = ["foo.sh"]
    for pattern in block_patterns:
        if pattern in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Command contains invalid pattern: {pattern}",
                }
            }
    return {}

options = ClaudeAgentOptions(
    allowed_tools=["Bash"],
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[check_bash_command]),
        ],
    }
)

async with ClaudeSDKClient(options=options) as client:
    # Test 1: Command with forbidden pattern (will be blocked)
    await client.query("Run the bash command: ./foo.sh --help")
    async for msg in client.receive_response():
        print(msg)

    print("\n" + "=" * 50 + "\n")

    # Test 2: Safe command that should work
    await client.query("Run the bash command: echo 'Hello from hooks example!'")
    async for msg in client.receive_response():
        print(msg)
```


## Types

See [src/claude_agent_sdk/types.py](src/claude_agent_sdk/types.py) for complete type definitions:
- `ClaudeAgentOptions` - Configuration options
- `AssistantMessage`, `UserMessage`, `SystemMessage`, `ResultMessage` - Message types
- `TextBlock`, `ToolUseBlock`, `ToolResultBlock` - Content blocks

## Error Handling

```python
from claude_agent_sdk import (
    ClaudeSDKError,      # Base error
    CLINotFoundError,    # Claude Code not installed
    CLIConnectionError,  # Connection issues
    ProcessError,        # Process failed
    CLIJSONDecodeError,  # JSON parsing issues
)

try:
    async for message in query(prompt="Hello"):
        pass
except CLINotFoundError:
    print("Please install Claude Code")
except ProcessError as e:
    print(f"Process failed with exit code: {e.exit_code}")
except CLIJSONDecodeError as e:
    print(f"Failed to parse response: {e}")
```

See [src/claude_agent_sdk/_errors.py](src/claude_agent_sdk/_errors.py) for all error types.

## Available Tools

See the [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/settings#tools-available-to-claude) for a complete list of available tools.

## Examples

See [examples/quick_start.py](examples/quick_start.py) for a complete working example.

See [examples/streaming_mode.py](examples/streaming_mode.py) for comprehensive examples involving `ClaudeSDKClient`. You can even run interactive examples in IPython from [examples/streaming_mode_ipython.py](examples/streaming_mode_ipython.py).

## Migrating from Claude Code SDK

If you're upgrading from the Claude Code SDK (versions < 0.1.0), please see the [CHANGELOG.md](CHANGELOG.md#010) for details on breaking changes and new features, including:

- `ClaudeCodeOptions` → `ClaudeAgentOptions` rename
- Merged system prompt configuration
- Settings isolation and explicit control
- New programmatic subagents and session forking features

## Development

If you're contributing to this project, run the initial setup script to install git hooks:

```bash
./scripts/initial-setup.sh
```

This installs a pre-push hook that runs lint checks before pushing, matching the CI workflow. To skip the hook temporarily, use `git push --no-verify`.

## License

MIT
