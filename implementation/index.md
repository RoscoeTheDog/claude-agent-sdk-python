# Implementation Sprint: Anthropic SDK OAuth Subscription Authentication
**Created**: 2025-11-04 23:43
**Status**: active
**Sprint Goal**: Enable claude-agent-sdk-python to use Claude Max subscription via OAuth tokens instead of pay-per-token API pricing

## Sprint Context

**Background**: Claude Code CLI successfully uses subscription authentication via OAuth tokens stored in `~/.claude/.credentials.json`. This sprint implements similar functionality for the Anthropic Python SDK (claude-agent-sdk-python fork).

**Key Technical Findings**:
- OAuth tokens: `sk-ant-oat01-...` (access), `sk-ant-ort01-...` (refresh)
- Credentials location: `~/.claude/.credentials.json`
- Scopes: `user:inference`, `user:profile`
- Token expiration: tracked via `expiresAt` timestamp
- Subscription type: stored in credentials (e.g., "max")

**Third-Party Precedent**: Cline, Repo Prompt, and Zed already integrate with Claude Code locally

---

## Stories

### Story 1: Research & Discovery
**Status**: unassigned
**Description**: Understand how Claude Code CLI authenticates with OAuth tokens and identify the API endpoints/headers used
**Acceptance Criteria**:
- [ ] Capture actual HTTP requests from Claude Code CLI using OAuth tokens
- [ ] Identify OAuth vs API key endpoint differences (if any)
- [ ] Document authentication header format (Bearer vs x-api-key)
- [ ] Understand token refresh flow and endpoint

### Story 1.1: Capture Claude Code CLI Network Traffic
**Status**: unassigned
**Parent**: Story 1
**Description**: Use network inspection tools to capture actual authentication requests from Claude Code CLI
**Technical Approach**: Use mitmproxy, Charles Proxy, or similar to intercept HTTPS traffic

### Story 1.2: Document Authentication Patterns
**Status**: unassigned
**Parent**: Story 1
**Description**: Create technical specification document for OAuth authentication flow based on captured traffic

### Story 2: OAuth Credentials Manager
**Status**: unassigned
**Description**: Implement module to read, validate, and refresh OAuth credentials from ~/.claude/.credentials.json
**Acceptance Criteria**:
- [ ] Read credentials from cross-platform path (~/.claude/.credentials.json)
- [ ] Validate token format (sk-ant-oat01-, sk-ant-ort01-)
- [ ] Check token expiration (expiresAt < current_time)
- [ ] Handle missing/corrupted credentials gracefully
- [ ] Fallback to API key if no OAuth credentials exist

### Story 2.1: Credentials File Reader
**Status**: unassigned
**Parent**: Story 2
**Description**: Implement function to locate and parse credentials JSON file
**Acceptance Criteria**:
- [ ] Cross-platform path resolution (Windows/Linux/macOS)
- [ ] JSON parsing with error handling
- [ ] Extract claudeAiOauth object
- [ ] Validate required fields (accessToken, refreshToken, expiresAt, scopes)

### Story 2.2: Token Expiration Checker
**Status**: unassigned
**Parent**: Story 2
**Description**: Implement logic to check if access token is expired
**Acceptance Criteria**:
- [ ] Compare expiresAt timestamp with current time
- [ ] Add buffer (e.g., 5 minutes) to prevent edge cases
- [ ] Return boolean: token_is_valid

### Story 3: OAuth Token Refresh
**Status**: unassigned
**Description**: Implement token refresh mechanism using refreshToken when accessToken expires
**Acceptance Criteria**:
- [ ] Identify OAuth token refresh endpoint
- [ ] Send refresh request with refreshToken
- [ ] Parse new accessToken and expiresAt from response
- [ ] Update ~/.claude/.credentials.json with new tokens
- [ ] Handle refresh token expiration/invalidation errors

### Story 3.1: Research Token Refresh Endpoint
**Status**: unassigned
**Parent**: Story 3
**Description**: Discover the OAuth token refresh endpoint used by Claude Code CLI (via network capture or code inspection)

### Story 3.2: Implement Refresh Logic
**Status**: unassigned
**Parent**: Story 3
**Description**: Create async function to refresh tokens and persist to credentials file

### Story 4: Modify SDK HTTP Client
**Status**: unassigned
**Description**: Patch the Anthropic SDK's HTTP client to use OAuth Bearer tokens instead of x-api-key header
**Acceptance Criteria**:
- [ ] Detect authentication mode (OAuth vs API key)
- [ ] Set correct Authorization header format
- [ ] Replace x-api-key header when using OAuth
- [ ] Handle endpoint URL differences (if any)
- [ ] Maintain backward compatibility with API key auth

### Story 4.1: Authentication Mode Detection
**Status**: unassigned
**Parent**: Story 4
**Description**: Implement logic to determine whether to use OAuth or API key authentication
**Acceptance Criteria**:
- [ ] Check for ANTHROPIC_API_KEY env var
- [ ] Check for CLAUDE_USE_SUBSCRIPTION=true env var
- [ ] Check for valid OAuth credentials in ~/.claude/.credentials.json
- [ ] Priority: env var override > OAuth credentials > API key

### Story 4.2: HTTP Header Injection
**Status**: unassigned
**Parent**: Story 4
**Description**: Modify SDK's HTTP client to inject OAuth Bearer token when in subscription mode

### Story 5: Integration & Testing
**Status**: unassigned
**Description**: Test the complete OAuth authentication flow end-to-end
**Acceptance Criteria**:
- [ ] Test with valid OAuth credentials (fresh token)
- [ ] Test with expired OAuth credentials (trigger refresh)
- [ ] Test fallback to API key when OAuth unavailable
- [ ] Test error handling (corrupted credentials, refresh failure)
- [ ] Verify actual API calls are counted against subscription, not API credits

### Story 5.1: Unit Tests
**Status**: unassigned
**Parent**: Story 5
**Description**: Write unit tests for credentials manager, token refresh, and authentication mode selection

### Story 5.2: Integration Tests
**Status**: unassigned
**Parent**: Story 5
**Description**: Write integration tests that make actual API calls using OAuth tokens

### Story 5.3: Manual Verification
**Status**: unassigned
**Parent**: Story 5
**Description**: Manually verify subscription usage is deducted (not API credits) via Claude dashboard

### Story 6: Documentation & Polish
**Status**: unassigned
**Description**: Document OAuth authentication setup and usage for end users
**Acceptance Criteria**:
- [ ] README section explaining OAuth authentication
- [ ] Setup instructions (how to enable subscription mode)
- [ ] Troubleshooting guide (common errors)
- [ ] Code examples showing both auth modes
- [ ] Update docstrings for modified functions

---

## Progress Log

### 2025-11-04 23:43 - Sprint Started
- Created sprint structure
- Defined 6 major stories with 11 sub-stories
- Sprint initialized in claude-agent-sdk-python project
- Context loaded from Graphiti memory (anthropic_sdk_oauth_project group)

---

## Sprint Summary
{To be filled upon completion}
