# Story 1.1: Capture Claude Code CLI Network Traffic - SUPERSEDED

**Status**: Superseded by Story 1 findings
**Date**: 2025-11-05
**Parent**: Story 1

## Reason for Superseding

Story 1.1 (network traffic capture) is **NOT NEEDED** based on Story 1 research findings.

## Why Network Capture is Unnecessary

### 1. SDK Architecture

The Python SDK does NOT communicate directly with Anthropic's API servers:

```
Python SDK → Claude CLI (subprocess) → Anthropic API
     ↑              ↑                        ↑
   JSON-RPC    OAuth/API Key          HTTPS (handled by CLI)
```

- **Python SDK** talks to **Claude CLI** via stdin/stdout (JSON-RPC)
- **Claude CLI** talks to **Anthropic API** via HTTPS (OAuth or API key)
- **We only control the subprocess environment**, not the HTTP layer

### 2. Claude CLI Handles All OAuth Protocol

From Story 1 findings:
- Claude CLI reads `~/.claude/.credentials.json` automatically
- Claude CLI handles token refresh internally
- Claude CLI manages OAuth header injection
- Claude CLI decides when to refresh based on `expiresAt`

**We don't implement OAuth protocol → We don't need to capture it**

### 3. Environment Variable Approach Sufficient

Story 1 identified the complete implementation strategy:

```python
# All we need to do:
env = os.environ.copy()
env.pop("ANTHROPIC_API_KEY", None)  # Force OAuth mode
env["CLAUDE_USE_SUBSCRIPTION"] = "true"  # Optional flag

subprocess.Popen(["claude", "code"], env=env, ...)
```

Claude CLI handles everything else internally.

### 4. Token Refresh Endpoint Not Needed

**Question**: Do we need to know the token refresh endpoint?
**Answer**: **NO**

- Token refresh is handled by Claude CLI, not our SDK
- We never make direct HTTP requests to Anthropic's OAuth endpoints
- Our responsibility ends at subprocess environment configuration

## What Story 1 Already Provided

✅ Authentication header formats (Bearer vs x-api-key)
✅ API endpoint confirmation (same for both auth types)
✅ Environment variable configuration
✅ Credentials file location and structure
✅ Implementation strategy (delegate to Claude CLI)
✅ No protocol changes needed (JSON-RPC stays same)

## Remaining Unknowns (Acceptable)

The following are unknown but **NOT BLOCKING** implementation:

1. **Exact token refresh endpoint**: Claude CLI handles this internally
2. **Refresh request payload**: Claude CLI constructs this
3. **Refresh response parsing**: Claude CLI processes this
4. **Token expiration buffer logic**: Claude CLI implements this

**Why acceptable**: These are Claude CLI's internal implementation details. We trust Claude CLI to handle OAuth correctly.

## Implementation Path Forward

**Skip Story 1.1** and proceed directly to:

### Story 2: OAuth Credentials Manager
- Read `~/.claude/.credentials.json`
- Validate token presence and format
- Check expiration status
- **Delegate refresh to Claude CLI** (not our responsibility)

### Story 3: Browser OAuth Flow
- Detect missing/expired credentials
- Trigger `claude setup-token` command
- OR implement browser flow ourselves (fallback)

## Decision

**Mark Story 1.1 as SUPERSEDED**

- No network capture needed
- No traffic analysis needed
- Story 1 findings are complete and sufficient
- Move to Story 2 (Credentials Manager)

## Alternative: Network Capture for Documentation Only

If we wanted to capture traffic for **educational/documentation purposes** (not implementation):

```bash
# Install mitmproxy
pip install mitmproxy

# Start proxy
mitmproxy --mode regular --listen-port 8080

# Configure proxy for Claude CLI
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080

# Run Claude CLI
claude code "test prompt"

# Observe traffic in mitmproxy UI
```

However, this provides **NO VALUE** for our implementation since:
- We don't make these HTTP requests ourselves
- We delegate to Claude CLI
- Understanding the protocol doesn't change our code

## Recommendation

1. Mark Story 1.1 as **superseded**
2. Mark Story 1.2 as **superseded** (same reasoning)
3. Proceed to **Story 2** (OAuth Credentials Manager)
4. Update sprint index with superseded status

---

**Author**: Claude (Agent)
**Date**: 2025-11-05
**Confidence**: Very High (95%)
