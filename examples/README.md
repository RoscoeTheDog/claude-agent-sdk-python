# Claude Agent SDK Examples

This folder contains examples demonstrating various features of the Claude Agent SDK.

## 📚 Available Examples

- **[Pretty Printer Demos](#pretty-printer-demos)** - Message rendering and formatting (NEW!)
- **[OAuth Authentication](#oauth-authentication)** - Using Claude subscription credentials
- **[Other Examples](#other-examples)** - Various SDK features

---

# Pretty Printer Demos

Interactive demonstrations of the message rendering system added in Sprint 1.

## Quick Start

### 30-Second Demo
```bash
python quick_demo.py
```
Shows the simplest usage with one line of code.

### Full Interactive Demo (5-10 minutes)
```bash
python demo_pretty_printer.py
```
Comprehensive showcase of all rendering features with 7 interactive demos.

### Menu Launcher
```bash
./run_demo.sh
# or on Windows Git Bash:
bash run_demo.sh
```
Interactive menu to choose which demo to run.

## What's Included

- **quick_demo.py** - Minimal 30-second demo
- **demo_pretty_printer.py** - Full feature showcase with 7 demos
- **pretty_printer_basic.py** - Code examples and usage patterns
- **run_demo.sh** - Interactive launcher script
- **DEMO_README.md** - Complete demo guide with troubleshooting

## Features Demonstrated

1. Simple `display_message()` usage
2. Render levels (MINIMAL, STANDARD, DETAILED)
3. Multiple destinations (console + file)
4. Custom configuration
5. Tool use formatting
6. UTF-8 character rendering
7. Before/after comparison

For complete documentation, see `DEMO_README.md` in this folder.

---

# OAuth Authentication

Examples demonstrating OAuth authentication with the Claude Agent SDK.

## Prerequisites

1. **Claude Code CLI installed**:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **OAuth credentials** (one-time setup):
   ```bash
   claude /login
   ```
   This will open your browser to authenticate with your Claude Max/Pro subscription.

## Setup

The virtual environment has already been created for you! If you need to recreate it:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows (Git Bash/MSYS):
source venv/Scripts/activate
# Windows (Command Prompt):
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install the SDK in editable mode
pip install -e ..
```

## Running the Examples

### Simple Demo (Recommended for first-time users)

The simplest possible OAuth example:

```bash
# Windows (Git Bash/MSYS):
./venv/Scripts/python.exe oauth_simple.py

# Windows (Command Prompt):
venv\Scripts\python.exe oauth_simple.py

# macOS/Linux:
./venv/bin/python oauth_simple.py
```

**What it does**: Sends a simple query using your OAuth credentials automatically.

### Comprehensive Demo

Full-featured demo with multiple examples:

```bash
# Windows (Git Bash/MSYS):
./venv/Scripts/python.exe oauth_demo.py

# Windows (Command Prompt):
venv\Scripts\python.exe oauth_demo.py

# macOS/Linux:
./venv/bin/python oauth_demo.py
```

**What it includes**:
- OAuth credentials status checker
- Basic OAuth query (auto-detect)
- Explicit OAuth mode (no fallback)
- OAuth with file operations (Read/Write tools)

## Examples Overview

### oauth_simple.py
- **Lines of code**: ~10
- **Complexity**: Minimal
- **Use case**: Quick test to verify OAuth is working

### oauth_demo.py
- **Lines of code**: ~170
- **Complexity**: Comprehensive
- **Use case**: Learn all OAuth configuration options and features

## Troubleshooting

**Error: "OAuth credentials not found"**
```bash
# Solution: Run the login command
claude /login
```

**Error: "Claude Code not installed"**
```bash
# Solution: Install Claude Code CLI
npm install -g @anthropic-ai/claude-code
```

**Error: "Module not found"**
```bash
# Solution: Install SDK in the virtual environment
./venv/Scripts/python.exe -m pip install -e ..
```

## Understanding OAuth vs API Key

When you run these examples with OAuth credentials:
- ✅ Your usage counts against your Claude subscription (Max/Pro)
- ✅ No API credits are consumed
- ✅ Tokens auto-refresh automatically
- ✅ SDK uses `~/.claude/.credentials.json`

Without OAuth credentials (fallback to API key):
- Uses `ANTHROPIC_API_KEY` environment variable
- Pay-per-token pricing
- No subscription benefits

## Configuration Options

You can customize authentication behavior:

```python
from claude_agent_sdk import ClaudeAgentOptions

# Force OAuth only (fail if unavailable)
options = ClaudeAgentOptions(
    auth_mode="oauth",
    auth_fallback=False
)

# CI/CD mode (no browser login)
options = ClaudeAgentOptions(
    auth_interactive=False,
    auth_fallback=True
)

# See oauth_demo.py for more examples
```

## Environment Variables

Control authentication via environment variables:

```bash
# Force OAuth mode
export CLAUDE_AUTH_MODE=oauth

# Disable fallback to API key
export CLAUDE_AUTH_FALLBACK=false

# Disable interactive browser login (for CI/CD)
export CLAUDE_AUTH_INTERACTIVE=false
```

See the main [README.md](../README.md#authentication) for complete documentation.

---

# Other Examples

Additional examples demonstrating various SDK features:

- **quick_start.py** - Basic SDK usage and queries
- **streaming_mode.py** - Streaming responses with async iteration
- **hooks.py** - Custom hooks for tool calls and permissions
- **agents.py** - Multi-agent workflows
- **mcp_calculator.py** - MCP (Model Context Protocol) integration
- **tool_permission_callback.py** - Custom tool permission handling
- **system_prompt.py** - Custom system prompts
- **max_budget_usd.py** - Budget limits and cost control

Run any example with:
```bash
python <example_name>.py
```
