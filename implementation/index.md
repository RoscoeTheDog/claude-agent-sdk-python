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
**Status**: completed
**Claimed**: 2025-11-05 09:30
**Completed**: 2025-11-05 09:45
**Description**: Understand how Claude Code CLI authenticates with OAuth tokens and identify the API endpoints/headers used
**Acceptance Criteria**:
- [x] Capture actual HTTP requests from Claude Code CLI using OAuth tokens
- [x] Identify OAuth vs API key endpoint differences (if any)
- [x] Document authentication header format (Bearer vs x-api-key)
- [x] Understand token refresh flow and endpoint (partial - hypothesis documented)
**Findings**: See `implementation/stories/story-1-research-findings.md`

### Story 1.1: Capture Claude Code CLI Network Traffic
**Status**: superseded
**Claimed**: 2025-11-05 09:50
**Completed**: 2025-11-05 09:55
**Parent**: Story 1
**Description**: Use network inspection tools to capture actual authentication requests from Claude Code CLI
**Technical Approach**: Use mitmproxy, Charles Proxy, or similar to intercept HTTPS traffic
**Reason**: SDK communicates with Claude CLI (subprocess), not directly with Anthropic API. Claude CLI handles all OAuth protocol internally. Network capture provides no implementation value. See `story-1.1-superseded.md`

### Story 1.2: Document Authentication Patterns
**Status**: superseded
**Parent**: Story 1
**Description**: Create technical specification document for OAuth authentication flow based on captured traffic
**Reason**: Story 1 findings document already provides all necessary authentication patterns. No additional traffic capture needed.

### Story 2: OAuth Credentials Manager
**Status**: completed
**Claimed**: 2025-11-05 10:00
**Completed**: 2025-11-05 10:15
**Description**: Implement module to read, validate, and refresh OAuth credentials from ~/.claude/.credentials.json
**Acceptance Criteria**:
- [x] Read credentials from cross-platform path (~/.claude/.credentials.json)
- [x] Validate token format (sk-ant-oat01-, sk-ant-ort01-)
- [x] Check token expiration (expiresAt < current_time)
- [x] Handle missing/corrupted credentials gracefully
- [x] Fallback to API key if no OAuth credentials exist (via get_valid_credentials())
**Implementation**: `src/claude_agent_sdk/_internal/oauth_credentials.py`
**Tests**: `tests/test_oauth_credentials.py` (25 tests, all passing)

### Story 2.1: Credentials File Reader
**Status**: superseded
**Parent**: Story 2
**Description**: Implement function to locate and parse credentials JSON file
**Reason**: Completed as part of Story 2 implementation (read_credentials() function)

### Story 2.2: Token Expiration Checker
**Status**: superseded
**Parent**: Story 2
**Description**: Implement validation logic to check if OAuth access token has expired based on timestamp comparison
**Reason**: Completed as part of Story 2 implementation (OAuthCredentials.is_expired property with 5-minute buffer)

### Story 3: Browser-Based OAuth Login Flow
**Status**: completed
**Claimed**: 2025-11-05 10:20
**Completed**: 2025-11-05 11:00
**Description**: Implement browser-based OAuth authentication flow (like Claude Code CLI) when no valid credentials exist
**Acceptance Criteria**:
- [x] Detect when OAuth login is needed (no credentials, expired refresh token)
- [x] Launch browser OAuth flow (delegated to Claude CLI)
- [x] Trigger `claude /login` command for authentication
- [x] Verify credentials created successfully
- [x] Display user-friendly login prompts
- [x] Handle login failures gracefully
**Implementation**: Delegation strategy using `claude /login` command
**Tests**: `tests/test_oauth_login.py` (21 tests, all passing)

### Story 3.1: Research OAuth Authorization Flow
**Status**: completed
**Claimed**: 2025-11-05 10:20
**Completed**: 2025-11-05 10:35
**Parent**: Story 3
**Description**: Reverse engineer Claude Code CLI's OAuth flow to identify endpoints and parameters
**Acceptance Criteria**:
- [x] Find OAuth authorization URL and required parameters - **Result**: Delegation strategy, endpoints not needed
- [x] Identify token exchange endpoint - **Result**: Handled by Claude CLI
- [x] Determine callback URL pattern - **Result**: Handled by Claude CLI
- [x] Document OAuth scopes needed (user:inference, user:profile) - **Result**: Handled by Claude CLI automatically
**Findings**: See `implementation/stories/story-3.1-oauth-flow-research.md`

### Story 3.2: Implement Browser OAuth Flow
**Status**: completed
**Claimed**: 2025-11-05 10:35
**Completed**: 2025-11-05 10:50
**Parent**: Story 3
**Description**: Create interactive OAuth login system with browser launch and callback handling
**Acceptance Criteria**:
- [x] Trigger `claude /login` command to launch browser OAuth
- [x] Let Claude CLI handle callback and token exchange
- [x] Verify credentials saved to ~/.claude/.credentials.json
- [x] Provide user-friendly prompts and error messages
- [x] Handle non-interactive mode gracefully
**Implementation**: `src/claude_agent_sdk/_internal/oauth_login.py`

### Story 3.3: Token Refresh Mechanism
**Status**: completed
**Claimed**: 2025-11-05 10:50
**Completed**: 2025-11-05 11:00
**Parent**: Story 3
**Description**: Implement automatic token refresh when access token expires (but refresh token still valid)
**Acceptance Criteria**:
- [x] Detect when token refresh is needed (expiring soon or expired)
- [x] Trigger Claude CLI auto-refresh by running harmless commands
- [x] Verify credentials were updated after refresh
- [x] Fall back to browser login if auto-refresh fails
- [x] Support both interactive and non-interactive modes
**Implementation**: `src/claude_agent_sdk/_internal/oauth_refresh.py`
**Tests**: `tests/test_oauth_refresh.py` (25 tests, all passing)

### Story 4: Authentication Configuration System
**Status**: completed
**Claimed**: 2025-11-05 11:10
**Completed**: 2025-11-05 11:45
**Description**: Implement hierarchical configuration system for auth method priority and fallback behavior
**Acceptance Criteria**:
- [x] Support CLAUDE_AUTH_MODE (auto|oauth|api_key)
- [x] Support CLAUDE_AUTH_FALLBACK (true|false) - allow fallback to API key
- [x] Support CLAUDE_AUTH_STRICT (true|false) - fail fast with no fallback
- [x] Support CLAUDE_AUTH_INTERACTIVE (true|false) - allow browser login
- [x] Programmatic config via ClaudeAgentOptions
- [x] Environment variables override SDK config
- [x] Clear error messages explaining auth failures and resolution steps
**Implementation**: `src/claude_agent_sdk/_internal/auth_config.py`
**Tests**: `tests/test_auth_config.py` (38 tests, all passing)

### Story 4.1: Configuration Schema
**Status**: superseded
**Parent**: Story 4
**Description**: Define configuration schema for authentication options
**Reason**: Completed as part of Story 4 implementation (AuthMode, AuthFallbackPolicy enums, ClaudeAgentOptions fields)

### Story 4.2: Priority Chain Implementation
**Status**: superseded
**Parent**: Story 4
**Description**: Implement configurable authentication priority and fallback chain
**Reason**: Completed as part of Story 4 implementation (load_auth_config with precedence handling)

### Story 5: Smart Authentication Manager
**Status**: unassigned
**Description**: Implement intelligent authentication system that auto-detects, refreshes, and prompts for login when needed
**Acceptance Criteria**:
- [ ] Auto-detect authentication mode using config from Story 4
- [ ] Check token validity before each request
- [ ] Auto-refresh expired access tokens (using refresh token)
- [ ] Auto-trigger browser login if refresh token expired (unless non-interactive)
- [ ] Respect fallback policy (error vs fallback to API key)
- [ ] Seamless user experience with minimal prompts

### Story 5.1: Authentication State Machine
**Status**: unassigned
**Parent**: Story 5
**Description**: Create state machine to manage authentication lifecycle with fallback support
**States**:
- API_KEY_MODE: Using ANTHROPIC_API_KEY (explicit or fallback)
- OAUTH_VALID: OAuth tokens valid, ready to use
- OAUTH_REFRESH_NEEDED: Access token expired, refresh token valid
- OAUTH_LOGIN_NEEDED: No credentials or refresh token expired
- AUTH_FAILED: All auth methods exhausted based on config
**Acceptance Criteria**:
- [ ] Implement state detection logic respecting config
- [ ] Define state transitions (OAUTH_REFRESH_NEEDED → OAUTH_VALID)
- [ ] Handle state transitions (OAUTH_FAILED → API_KEY_MODE if fallback enabled)
- [ ] Handle state actions (LOGIN_NEEDED → trigger browser flow or error based on config)
- [ ] Respect strict mode (error immediately on OAuth failure)

### Story 5.2: Pre-Request Authentication Check
**Status**: unassigned
**Parent**: Story 5
**Depends on**: Story 3.2, Story 3.3
**Description**: Hook into SDK's HTTP client to verify/refresh authentication before each API request
**Acceptance Criteria**:
- [ ] Intercept requests before sending
- [ ] Check token expiration (compare expiresAt with current time)
- [ ] Auto-refresh if needed (call Story 3.3 refresh logic)
- [ ] If refresh fails and interactive mode: prompt user to login (call Story 3.2 browser flow)
- [ ] If refresh fails and fallback enabled: switch to API key mode
- [ ] If refresh fails and strict mode: error with clear message
- [ ] User-friendly prompts: "Your session expired. Opening browser to login..." (interactive only)

### Story 6: Modify SDK HTTP Client
**Status**: unassigned
**Description**: Patch the Anthropic SDK's HTTP client to use OAuth Bearer tokens or API key based on active auth mode
**Acceptance Criteria**:
- [ ] Inject OAuth Bearer token into Authorization header (OAuth mode)
- [ ] Inject x-api-key header (API key mode)
- [ ] Switch headers dynamically if fallback occurs
- [ ] Handle endpoint URL differences (if any)
- [ ] Maintain backward compatibility with existing API key usage
- [ ] Log warnings when falling back from OAuth to API key

### Story 6.1: HTTP Header Injection
**Status**: unassigned
**Parent**: Story 6
**Description**: Modify SDK's HTTP client to inject appropriate auth headers based on current mode

### Story 7: Integration & Testing
**Status**: unassigned
**Description**: Test the complete authentication system with all configuration options and fallback scenarios
**Acceptance Criteria**:
- [ ] Test all auth modes (auto, oauth, api_key)
- [ ] Test all fallback policies (enabled, disabled, strict)
- [ ] Test interactive vs non-interactive modes
- [ ] Test browser login flow from scratch (no credentials)
- [ ] Test with valid OAuth credentials (fresh token)
- [ ] Test with expired access token (trigger auto-refresh)
- [ ] Test with expired refresh token (trigger browser login or fallback)
- [ ] Test fallback to API key when OAuth fails
- [ ] Test strict mode errors when fallback disabled
- [ ] Test non-interactive mode skips browser login
- [ ] Verify actual API calls are counted against subscription, not API credits

### Story 7.1: Configuration Tests
**Status**: unassigned
**Parent**: Story 7
**Description**: Test all configuration combinations and precedence
**Acceptance Criteria**:
- [ ] Test env var override of SDK config
- [ ] Test default configuration behavior
- [ ] Test priority chain with different configs
- [ ] Test error messages for invalid configs

### Story 7.2: OAuth Flow Tests
**Status**: unassigned
**Parent**: Story 7
**Description**: Test browser-based OAuth login and token management
**Acceptance Criteria**:
- [ ] Test initial login (no credentials file)
- [ ] Test callback server receives authorization code
- [ ] Test token exchange and persistence
- [ ] Test credentials file format and permissions

### Story 7.3: Fallback Behavior Tests
**Status**: unassigned
**Parent**: Story 7
**Description**: Test all fallback scenarios and error conditions
**Acceptance Criteria**:
- [ ] Test OAuth fails + fallback enabled + API key exists → use API key
- [ ] Test OAuth fails + fallback disabled → error with clear message
- [ ] Test OAuth fails + fallback enabled + no API key → error
- [ ] Test strict mode prevents any fallback
- [ ] Test warnings logged when falling back

### Story 7.4: Token Lifecycle Tests
**Status**: unassigned
**Parent**: Story 7
**Description**: Test automatic token refresh and expiration handling
**Acceptance Criteria**:
- [ ] Mock expired access token, verify auto-refresh
- [ ] Mock expired refresh token, verify browser login triggered (interactive)
- [ ] Mock expired refresh token, verify fallback used (non-interactive)
- [ ] Test concurrent requests don't cause duplicate refreshes
- [ ] Test refresh failures handled per config

### Story 7.5: Unit Tests
**Status**: unassigned
**Parent**: Story 7
**Description**: Write unit tests for credentials manager, state machine, config system, and authentication logic

### Story 7.6: Integration Tests
**Status**: unassigned
**Parent**: Story 7
**Description**: Write integration tests that make actual API calls using OAuth tokens

### Story 7.7: Manual Verification
**Status**: unassigned
**Parent**: Story 7
**Description**: Manually verify subscription usage is deducted (not API credits) via Claude dashboard

### Story 8: Documentation & Polish
**Status**: unassigned
**Description**: Document OAuth authentication setup, configuration options, and usage for end users
**Acceptance Criteria**:
- [ ] README section explaining OAuth authentication
- [ ] Configuration guide (all env vars and SDK options)
- [ ] Setup instructions for browser login flow
- [ ] Troubleshooting guide (common errors, re-login process)
- [ ] Code examples for all auth modes and configs
- [ ] Document fallback behavior and when it occurs
- [ ] Document interactive vs non-interactive modes
- [ ] Document auto-refresh and smart detection features
- [ ] Update docstrings for modified functions
- [ ] User experience documentation (what to expect during login/refresh/fallback)

---

## Progress Log

### 2025-11-04 23:43 - Sprint Started
- Created sprint structure
- Defined 7 major stories with 16 sub-stories
- Sprint initialized in claude-agent-sdk-python project
- Context loaded from Graphiti memory (anthropic_sdk_oauth_project group)

### 2025-11-04 23:58 - Sprint Plan Updated
- Added Story 3: Browser-Based OAuth Login Flow
- Added Story 4: Smart Authentication Manager with state machine
- Reorganized stories to include auto-detection and refresh
- Enhanced testing stories to cover full OAuth lifecycle
- Total: 7 major stories, 16 sub-stories
- Key features: Browser login, auto-refresh, smart detection

### 2025-11-05 00:05 - Added Authentication Configuration System
- Inserted Story 4: Authentication Configuration System
- Renumbered remaining stories (4→5, 5→6, 6→7, 7→8)
- Added hierarchical configuration with env vars + SDK options
- Added fallback policy: ENABLED, DISABLED, STRICT
- Added interactive vs non-interactive mode detection
- Created design doc: implementation/stories/auth-config-design.md
- Total: 8 major stories, 21 sub-stories
- Key features: Configurable fallback, strict mode, CI/CD support

---

## Sprint Summary
{To be filled upon completion}
