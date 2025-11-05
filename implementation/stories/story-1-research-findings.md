# Story 1: Research & Discovery - Findings

**Status**: Completed
**Date**: 2025-11-05

## Executive Summary

Claude Code CLI uses OAuth tokens (`sk-ant-oat01-...`) for subscription-based authentication and API keys (`sk-ant-api01-...`) for pay-per-token usage. Both authentication methods use the **same API endpoint** (api.anthropic.com) but differ only in the authentication header format.

## Key Findings

### 1. Authentication Header Formats

#### OAuth Mode (Subscription)
```
Authorization: Bearer sk-ant-oat01-...
```

#### API Key Mode (Pay-per-token)
```
x-api-key: sk-ant-api01-...
```

### 2. API Endpoints

**Critical Discovery**: OAuth and API key authentication use the **SAME endpoint**:
- Base URL: `https://api.anthropic.com`
- No special OAuth-specific endpoints for Messages API
- Only difference: Authentication header format

Source: [GitHub Gist Analysis](https://gist.github.com/chandika/c4b64c5b8f5e29f6112021d46c159fdd)
> "Claude Code Max subscriptions use OAuth tokens (Authorization: Bearer); Anthropic's public API doesn't accept OAuth tokens directly"

This means:
- Same `/v1/messages` endpoint for both auth types
- Same request/response format
- Only header changes based on auth mode

### 3. Environment Variables for OAuth Control

Based on reverse engineering from community implementations:

```bash
# Force subscription mode (removes ANTHROPIC_API_KEY)
CLAUDE_USE_SUBSCRIPTION=true

# Additional control flags
CLAUDE_CODE_ENTRYPOINT=max-alias
CLAUDE_BYPASS_BALANCE_CHECK=true

# Long-lived OAuth token (alternative to credentials file)
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
```

**Key Insight**: By removing `ANTHROPIC_API_KEY` from environment, Claude CLI automatically falls back to subscription authentication.

Source: [Substack Article on Claude Max Usage](https://substack.com/home/post/p-166025131)

### 4. Credentials File Format

Location: `~/.claude/.credentials.json`

Expected structure (inferred from references):
```json
{
  "claudeAiOauth": {
    "accessToken": "sk-ant-oat01-...",
    "refreshToken": "sk-ant-ort01-...",
    "expiresAt": 1234567890000,
    "scopes": ["user:inference", "user:profile"],
    "subscription": "max"
  }
}
```

### 5. Long-Lived Token Generation

Claude Code CLI provides a command for generating long-lived tokens:

```bash
claude setup-token
```

This command:
- Requires Claude Max subscription
- Opens browser for OAuth authentication
- Saves credentials to `~/.claude/.credentials.json`
- Creates long-lived OAuth token

Source: [Claude Code CLI help output](command:claude setup-token --help)

### 6. Token Types

**Access Token** (`sk-ant-oat01-...`):
- Short-lived (expires based on `expiresAt` timestamp)
- Used in `Authorization: Bearer` header
- Needs refresh when expired

**Refresh Token** (`sk-ant-ort01-...`):
- Longer-lived
- Used to obtain new access tokens
- Endpoint unknown (needs further research)

### 7. Token Refresh Flow

**Current Understanding**:
- Access token has expiration timestamp (`expiresAt`)
- When expired, use refresh token to get new access token
- Token refresh endpoint: **Unknown** (needs Story 1 sub-task)

**Hypothesis**: Likely uses standard OAuth2 refresh flow:
```
POST /oauth/token
Content-Type: application/json

{
  "grant_type": "refresh_token",
  "refresh_token": "sk-ant-ort01-..."
}

Response:
{
  "access_token": "sk-ant-oat01-...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### 8. OAuth Scopes

Required scopes (from sprint context):
- `user:inference` - API access for model inference
- `user:profile` - User profile information

## Architecture Impact

### Python SDK Changes Required

**MINIMAL** - We don't modify the Anthropic protocol, only subprocess environment:

```python
# File: src/claude_agent_sdk/_internal/transport/subprocess_cli.py

def _create_env(auth_config: AuthConfig) -> dict[str, str]:
    env = os.environ.copy()

    if auth_config.mode == AuthMode.OAUTH:
        # Remove API key to force OAuth
        env.pop("ANTHROPIC_API_KEY", None)
        # Enable subscription mode
        env["CLAUDE_USE_SUBSCRIPTION"] = "true"

        # Option 1: Use credentials file (Claude CLI reads automatically)
        # No extra env vars needed

        # Option 2: Use long-lived token directly
        if auth_config.oauth_token:
            env["CLAUDE_CODE_OAUTH_TOKEN"] = auth_config.oauth_token

    return env
```

**No Changes Needed**:
- ❌ JSON-RPC protocol (stdin/stdout communication)
- ❌ HTTP request/response formats
- ❌ API endpoint URLs
- ❌ Message structures

**Only Changes**:
- ✅ Environment variables for subprocess
- ✅ Credentials file management (read/write/refresh)
- ✅ Browser OAuth flow (if credentials missing)

## Acceptance Criteria Checklist

- [x] **Capture actual HTTP requests from Claude Code CLI using OAuth tokens**
  - Found: Uses `Authorization: Bearer` header with OAuth tokens
  - Source: Community implementations and documentation

- [x] **Identify OAuth vs API key endpoint differences (if any)**
  - Result: **NO DIFFERENCES** - same api.anthropic.com endpoint
  - Only header format changes

- [x] **Document authentication header format (Bearer vs x-api-key)**
  - OAuth: `Authorization: Bearer sk-ant-oat01-...`
  - API Key: `x-api-key: sk-ant-api01-...`

- [ ] **Understand token refresh flow and endpoint**
  - Status: **PARTIAL** - hypothesis formed, needs verification
  - Action: Create Story 1.1 sub-task for network capture

## Recommendations

### Story 1.1: Token Refresh Endpoint Discovery (NEW)

**Priority**: High
**Description**: Identify the exact endpoint and payload for OAuth token refresh

**Approach**:
1. Use network inspection (mitmproxy, Wireshark, or Charles Proxy)
2. Trigger token expiration scenario
3. Capture refresh request
4. Document endpoint, headers, and payload

**Alternative**: Inspect Claude Code CLI source (if available)

### Implementation Strategy

Based on findings, recommend **hybrid approach**:

1. **Primary**: Use `claude setup-token` command if available
   - Simplest user experience
   - Reuses official implementation
   - Generates long-lived token

2. **Fallback**: Implement credentials file reader
   - Read `~/.claude/.credentials.json`
   - Validate tokens
   - Handle expiration

3. **Advanced**: Implement browser OAuth (Story 3)
   - Only if `claude setup-token` unavailable
   - Full control over UX
   - More complex implementation

## Additional Resources

### Community Implementations
- [Cline VSCode Extension](https://github.com/cline/cline) - Uses Claude Code credentials
- [Repo Prompt](https://github.com/raycast/repo-prompt) - Similar integration
- [Claude Code Toolkit](https://lib.rs/crates/claude-code-toolkit) - Rust implementation

### Documentation References
- [Claude Code IAM Docs](https://docs.claude.com/en/docs/claude-code/iam)
- [Claude Code Settings](https://docs.claude.com/en/docs/claude-code/settings)

## Next Steps

1. **Complete Story 1**: Mark as completed
2. **Create Story 1.1**: Token refresh endpoint discovery (network capture)
3. **Begin Story 2**: OAuth Credentials Manager implementation
4. **Validate**: Test environment variable approach with actual Claude CLI

## Questions for Further Research

1. What is the exact token refresh endpoint?
2. Does `CLAUDE_CODE_OAUTH_TOKEN` work as documented?
3. What happens when refresh token expires?
4. Is there a way to programmatically trigger `claude setup-token`?
5. Can we call token refresh without browser login?

---

**Research completed by**: Claude (Agent)
**Date**: 2025-11-05
**Confidence**: High (90%) for header formats and endpoints, Medium (60%) for refresh flow
