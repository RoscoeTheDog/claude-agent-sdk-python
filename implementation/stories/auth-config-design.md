# Authentication Configuration Design

## Problem Statement

When both OAuth credentials and ANTHROPIC_API_KEY exist, we need user control over:
1. **Priority**: Which auth method to try first
2. **Fallback**: Whether to fall back on failure or error out
3. **Degradation chain**: Define the exact sequence of auth attempts

## Configuration Options

### Option 1: Environment Variables (Simple)

```bash
# Primary auth method
CLAUDE_AUTH_MODE=oauth|api_key|auto  # Default: auto

# Fallback behavior
CLAUDE_AUTH_FALLBACK=true|false  # Default: true

# Strict mode (no fallback, fail fast)
CLAUDE_AUTH_STRICT=true|false  # Default: false
```

**Behavior**:
- `CLAUDE_AUTH_MODE=oauth` + `CLAUDE_AUTH_FALLBACK=false` → OAuth only, error if fails
- `CLAUDE_AUTH_MODE=oauth` + `CLAUDE_AUTH_FALLBACK=true` → OAuth first, API key if OAuth fails
- `CLAUDE_AUTH_MODE=api_key` → Always use API key, ignore OAuth
- `CLAUDE_AUTH_MODE=auto` → Smart detection (OAuth if available, else API key)

### Option 2: SDK Configuration (Programmatic)

```python
from claude_agent_sdk import ClaudeAgentOptions, AuthMode, AuthFallbackPolicy

options = ClaudeAgentOptions(
    auth_mode=AuthMode.OAUTH,  # or AuthMode.API_KEY, AuthMode.AUTO
    auth_fallback=AuthFallbackPolicy.DISABLED,  # or ENABLED, STRICT
    auth_priority_chain=["oauth", "api_key"],  # Custom chain
)

client = ClaudeSDKClient(options=options)
```

### Option 3: Hybrid (Recommended)

Environment variables override SDK config:

```python
# In code
options = ClaudeAgentOptions(
    auth_mode=AuthMode.AUTO,
    auth_fallback=AuthFallbackPolicy.ENABLED
)

# User sets: CLAUDE_AUTH_STRICT=true
# Result: Overrides auth_fallback to DISABLED
```

## Degradation Chains

### Chain 1: OAuth-First with Fallback (Default)
```
1. Check ANTHROPIC_API_KEY env var
   - If set AND (CLAUDE_AUTH_MODE=api_key OR CLAUDE_USE_API_KEY=true)
     → Use API key mode (skip OAuth)

2. Try OAuth
   - Check ~/.claude/.credentials.json exists
   - Check access token not expired
   - If expired, try refresh
   - If refresh fails, try browser login (if interactive)
   - If OAuth succeeds → use OAuth

3. Fallback to API key (if CLAUDE_AUTH_FALLBACK=true)
   - Check ANTHROPIC_API_KEY env var
   - If set → use API key
   - If not set → ERROR: No authentication available
```

### Chain 2: API Key Only (No OAuth)
```
User sets: CLAUDE_AUTH_MODE=api_key

1. Check ANTHROPIC_API_KEY env var
   - If set → use API key
   - If not set → ERROR: ANTHROPIC_API_KEY not set
```

### Chain 3: OAuth Strict (No Fallback)
```
User sets: CLAUDE_AUTH_MODE=oauth, CLAUDE_AUTH_FALLBACK=false

1. Try OAuth
   - Check credentials, refresh, browser login
   - If OAuth succeeds → use OAuth
   - If OAuth fails → ERROR: OAuth authentication failed, no fallback allowed
```

### Chain 4: Non-Interactive (Server/CI Mode)
```
User sets: CLAUDE_AUTH_INTERACTIVE=false

1. Try OAuth
   - Check credentials
   - Try refresh if expired
   - DO NOT trigger browser login (non-interactive)
   - If OAuth succeeds → use OAuth

2. Fallback to API key (if enabled)
   - Check ANTHROPIC_API_KEY
   - If set → use API key
   - If not set → ERROR: No valid authentication (non-interactive mode)
```

## Error Handling

### Scenario: OAuth fails, no API key, fallback enabled
```
ERROR: Authentication failed
- OAuth authentication failed: refresh token expired
- Attempted to fall back to API key mode
- ANTHROPIC_API_KEY environment variable not set
- No valid authentication method available

Suggestions:
1. Set ANTHROPIC_API_KEY environment variable
2. Run authentication flow: python -m claude_agent_sdk login
3. Set CLAUDE_AUTH_STRICT=false to disable fallback requirement
```

### Scenario: OAuth fails, API key exists, fallback disabled
```
ERROR: OAuth authentication failed (strict mode)
- Access token expired
- Refresh token invalid
- Browser login required but CLAUDE_AUTH_FALLBACK=false

To resolve:
1. Enable fallback: unset CLAUDE_AUTH_FALLBACK or set CLAUDE_AUTH_FALLBACK=true
2. Re-authenticate: python -m claude_agent_sdk login
3. Use API key: set CLAUDE_AUTH_MODE=api_key
```

## Recommended Default Configuration

```python
DEFAULT_CONFIG = {
    "auth_mode": "auto",  # Smart detection
    "auth_fallback": True,  # Allow fallback
    "auth_interactive": True,  # Allow browser login
    "auth_priority_chain": [
        "env_api_key_override",  # ANTHROPIC_API_KEY + explicit mode
        "oauth",                 # Try OAuth
        "api_key_fallback",      # Fall back to API key
    ]
}
```

### Priority Resolution Order

1. **Explicit user override**: `CLAUDE_AUTH_MODE=api_key` → skip OAuth entirely
2. **OAuth attempt**: Try OAuth (credentials → refresh → browser login)
3. **Fallback** (if enabled): Use ANTHROPIC_API_KEY if OAuth failed
4. **Error**: No auth available

## Implementation Notes

### Environment Variables to Support

```bash
# Core settings
ANTHROPIC_API_KEY=sk-ant-api...      # API key for fallback
CLAUDE_AUTH_MODE=auto|oauth|api_key  # Primary auth method
CLAUDE_AUTH_FALLBACK=true|false      # Allow fallback to API key
CLAUDE_AUTH_STRICT=true|false        # Fail fast, no fallback
CLAUDE_AUTH_INTERACTIVE=true|false   # Allow browser login

# Legacy compatibility
CLAUDE_USE_SUBSCRIPTION=true         # Alias for CLAUDE_AUTH_MODE=oauth
```

### Configuration Precedence

1. Environment variables (highest priority)
2. SDK ClaudeAgentOptions config
3. Default values

### Non-Interactive Detection

Auto-detect non-interactive environments:
- CI/CD: Check `CI=true`, `GITHUB_ACTIONS=true`, etc.
- No TTY: `sys.stdin.isatty() == False`
- Explicit: `CLAUDE_AUTH_INTERACTIVE=false`

If non-interactive detected:
- Skip browser login prompts
- Disable interactive token refresh
- Require pre-existing valid credentials or API key

## User Experience Examples

### Example 1: Developer with subscription (default)
```python
# No config needed
client = ClaudeSDKClient()
# → Uses OAuth, auto-refreshes, falls back to API key if needed
```

### Example 2: CI/CD pipeline (API key only)
```bash
export ANTHROPIC_API_KEY=sk-ant-api...
export CLAUDE_AUTH_MODE=api_key
```

### Example 3: Strict OAuth (no fallback)
```python
options = ClaudeAgentOptions(
    auth_mode=AuthMode.OAUTH,
    auth_fallback=AuthFallbackPolicy.DISABLED
)
client = ClaudeSDKClient(options=options)
# → OAuth only, errors if OAuth unavailable
```

### Example 4: Server application (non-interactive)
```bash
export CLAUDE_AUTH_INTERACTIVE=false
# → Uses pre-existing OAuth credentials, no browser prompts
# → Falls back to API key if OAuth invalid
# → Errors if browser login needed
```

## Security Considerations

1. **API Key Exposure**: Fallback to API key should log warning about switching from subscription to pay-per-token
2. **Token Refresh**: Failed refresh should not immediately trigger browser login in server environments
3. **Credential Storage**: Always use secure file permissions (0600) for ~/.claude/.credentials.json
4. **Audit Trail**: Log authentication method used for each session

## Testing Strategy

Test matrix:

| OAuth Valid | API Key Set | Mode      | Fallback | Expected Result           |
|-------------|-------------|-----------|----------|---------------------------|
| Yes         | Yes         | auto      | true     | Use OAuth                 |
| Yes         | Yes         | oauth     | false    | Use OAuth                 |
| Yes         | Yes         | api_key   | -        | Use API key               |
| No          | Yes         | auto      | true     | Use API key (fallback)    |
| No          | Yes         | oauth     | false    | Error (OAuth strict)      |
| No          | No          | auto      | true     | Error (no auth)           |
| Yes         | No          | auto      | true     | Use OAuth                 |
| Expired     | Yes         | auto      | true     | Refresh → fallback if fail|
