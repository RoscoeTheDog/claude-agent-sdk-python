# Protocol Analysis: Do We Need to Modify Communication Interfaces?

## Question
Do we need to modify the interfaces for the communication protocol to Anthropic's servers so they can authenticate OAuth?

## Answer: NO - We Don't Touch Anthropic's Servers Directly

### Current Architecture

```
┌─────────────────┐
│  Python SDK     │
│ (Our Code)      │
└────────┬────────┘
         │
         │ subprocess.Popen()
         │ stdin/stdout JSON-RPC
         │
┌────────▼────────┐
│  Claude Code    │  ← This is Anthropic's official CLI
│  CLI (@anthropic│     (already supports OAuth!)
│  -ai/claude-code│
└────────┬────────┘
         │
         │ HTTPS with auth headers
         │ (OAuth or API key)
         │
┌────────▼────────┐
│  Anthropic API  │
│  Servers        │
└─────────────────┘
```

### Key Insight
**The Python SDK does NOT talk to Anthropic servers directly!**

It talks to the **Claude Code CLI** via JSON-RPC (subprocess communication):
1. SDK → Claude CLI (stdin/stdout JSON messages)
2. Claude CLI → Anthropic API (HTTPS with auth)

### What This Means

**We DON'T Need To:**
- ❌ Modify HTTP protocol to Anthropic servers
- ❌ Change API request/response formats
- ❌ Implement OAuth protocol ourselves
- ❌ Handle HTTPS, TLS, or network layer

**We DO Need To:**
- ✅ Tell Claude CLI to use OAuth instead of API key
- ✅ Ensure Claude CLI has valid OAuth credentials
- ✅ Pass correct environment variables to Claude CLI subprocess

## How Claude CLI Already Works

### API Key Mode (Current)
```bash
# User sets this
export ANTHROPIC_API_KEY=sk-ant-api01-...

# SDK launches Claude CLI
claude code  # CLI sees ANTHROPIC_API_KEY env var

# CLI makes requests to Anthropic with x-api-key header
```

### OAuth Mode (What We're Implementing)
```bash
# User has ~/.claude/.credentials.json (from browser login)
# OR we trigger browser login to create it

# SDK launches Claude CLI WITHOUT ANTHROPIC_API_KEY
claude code  # CLI checks ~/.claude/.credentials.json

# CLI makes requests to Anthropic with Authorization: Bearer <oauth-token>
```

## What Changes in Our Implementation

### File: `src/claude_agent_sdk/_internal/transport/subprocess_cli.py`

**Current code** (simplified):
```python
def _create_env() -> dict[str, str]:
    env = os.environ.copy()
    # Claude CLI picks up ANTHROPIC_API_KEY from env
    return env

subprocess.Popen(
    ["claude", "code"],
    env=_create_env(),
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
)
```

**Modified code** (OAuth support):
```python
def _create_env(auth_config: AuthConfig) -> dict[str, str]:
    env = os.environ.copy()

    if auth_config.mode == AuthMode.OAUTH:
        # Remove API key to force OAuth mode
        env.pop("ANTHROPIC_API_KEY", None)
        # Set subscription mode flag
        env["CLAUDE_USE_SUBSCRIPTION"] = "true"
    elif auth_config.mode == AuthMode.API_KEY:
        # Ensure API key is set
        if "ANTHROPIC_API_KEY" not in env:
            raise AuthError("ANTHROPIC_API_KEY not set")

    return env
```

**That's it!** Claude CLI handles everything else.

## Protocol Interface Changes: NONE

### What Stays The Same

1. **JSON-RPC Messages**: No change
   ```json
   {
     "jsonrpc": "2.0",
     "method": "query",
     "params": {"prompt": "Hello"}
   }
   ```

2. **Claude CLI Communication**: No change
   - Still use stdin/stdout
   - Still use same subprocess.Popen
   - Still use same JSON-RPC protocol

3. **Anthropic API Protocol**: No change (handled by CLI)
   - Claude CLI handles OAuth vs API key
   - Claude CLI handles token refresh
   - Claude CLI handles HTTPS requests

### What Changes

**Only environment variables** passed to Claude CLI subprocess:
- `ANTHROPIC_API_KEY` (present or absent)
- `CLAUDE_USE_SUBSCRIPTION` (optional flag)
- `CLAUDE_AUTH_MODE` (optional, for our config)

## Browser OAuth Flow: Where Does It Happen?

### Option A: Let Claude CLI Handle It (Recommended)

```python
# User runs SDK
client = ClaudeSDKClient()

# SDK checks ~/.claude/.credentials.json
if not valid_oauth_creds():
    # Launch Claude CLI in auth mode
    subprocess.run(["claude", "login"])
    # This opens browser, user logs in, tokens saved
    # Then we proceed with normal SDK usage
```

**Pros**:
- Claude CLI already has browser OAuth flow
- We reuse their implementation
- Less code for us to write

**Cons**:
- Separate command to run first
- User experience: two-step process

### Option B: Implement Browser OAuth Ourselves

```python
# SDK detects no valid OAuth
if not valid_oauth_creds():
    # We open browser ourselves
    oauth_flow = OAuthBrowserFlow()
    tokens = await oauth_flow.authenticate()
    save_credentials(tokens)

# Then launch Claude CLI with OAuth
```

**Pros**:
- Seamless one-step experience
- More control over UX

**Cons**:
- We must implement OAuth browser flow
- Duplicate Claude CLI's code
- More complex

### Recommendation: Hybrid Approach

**Story 3 implementation**:
1. Check if `claude login` command exists
2. If yes: Use it (Option A)
3. If no: Implement our own browser flow (Option B)

This gives us:
- Best UX when Claude CLI available
- Fallback when running in restricted environment

## What Story 1 Needs to Answer

### Critical Questions

1. **Does Claude CLI use same API endpoints for OAuth vs API key?**
   - Likely: YES (same api.anthropic.com)
   - Only difference: Authorization header

2. **What's the exact header format?**
   - API Key: `x-api-key: sk-ant-api01-...`
   - OAuth: `Authorization: Bearer sk-ant-oat01-...`

3. **Are there any OAuth-specific endpoints?**
   - Token refresh: `POST /oauth/refresh` (or similar)
   - Initial token exchange: `POST /oauth/token`

4. **Does OAuth use different base URL?**
   - API Key: `https://api.anthropic.com`
   - OAuth: Same or different? (need to verify)

### How to Answer These (Story 1.1)

**Method 1: Network Capture**
```bash
# Terminal 1: Start mitmproxy
mitmproxy --mode regular --listen-port 8080

# Terminal 2: Run Claude CLI through proxy
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080
claude code  # Make a request

# Observe requests in mitmproxy
```

**Method 2: Claude CLI Source Code**
```bash
# If Claude CLI is open source, inspect:
npm view @anthropic-ai/claude-code
# Look for OAuth implementation
```

**Method 3: Credential File Analysis**
```bash
# Run Claude CLI, capture traffic
# Compare API key vs OAuth requests
# Document differences
```

## Impact on Sprint Plan

### Already Covered ✅

- **Story 1**: Research & Discovery (answers protocol questions)
- **Story 3**: Browser OAuth (browser flow, we implement or delegate)
- **Story 6**: HTTP Client Modification (environment vars, not protocol)

### Potential Additions

**Story 1.3: Validate No Protocol Changes Needed**
**Status**: unassigned
**Parent**: Story 1
**Description**: Confirm Claude CLI handles all OAuth protocol, SDK only needs env vars
**Acceptance Criteria**:
- [ ] Verify same JSON-RPC protocol for OAuth vs API key
- [ ] Verify no changes needed to subprocess communication
- [ ] Document environment variables Claude CLI expects
- [ ] Confirm Claude CLI version supports OAuth (check minimum version)

### Not Needed ❌

- ❌ Story for "HTTP protocol modification"
- ❌ Story for "HTTPS client implementation"
- ❌ Story for "Anthropic API OAuth endpoints"
- ❌ Story for "Request/response format changes"

## Conclusion

**Do we need to modify communication protocol interfaces?**

**NO.** The Python SDK communicates with Claude CLI via JSON-RPC (subprocess stdin/stdout), which doesn't change. Claude CLI handles all OAuth protocol with Anthropic's servers. We only need to:

1. Manage OAuth credentials (`~/.claude/.credentials.json`)
2. Set correct environment variables for Claude CLI subprocess
3. Optionally implement browser OAuth flow (or delegate to `claude login`)

**This is already covered in the current sprint plan.**
