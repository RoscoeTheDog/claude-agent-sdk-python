# OAuth Demo Examples

This folder contains examples demonstrating OAuth authentication with the Claude Agent SDK.

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
