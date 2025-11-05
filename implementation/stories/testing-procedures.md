# Testing Procedures for OAuth Implementation

## Overview

Our testing strategy uses a **3-tier approach**:
1. **Unit Tests** - Fast, isolated, mocked
2. **Integration Tests** - Real API calls, real OAuth flow
3. **Manual Verification** - Dashboard verification, billing checks

## Testing Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: Unit Tests (~100 tests, <1min runtime)             │
│  ├─ Mock credentials files                                  │
│  ├─ Mock token expiration                                   │
│  ├─ Mock Claude CLI subprocess                              │
│  └─ Test state machine transitions                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2: Integration Tests (~20 tests, ~5min runtime)       │
│  ├─ Real OAuth credentials (test account)                   │
│  ├─ Real API calls to Anthropic                             │
│  ├─ Real browser OAuth flow (headless)                      │
│  └─ Real token refresh                                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 3: Manual Verification (~10 scenarios, ~30min)        │
│  ├─ Check Claude dashboard for subscription usage           │
│  ├─ Verify no API credits deducted                          │
│  ├─ Test browser login UX                                   │
│  └─ Cross-platform testing (Windows/Mac/Linux)              │
└─────────────────────────────────────────────────────────────┘
```

## Tier 1: Unit Tests

### Test Framework
```python
# pytest with fixtures
import pytest
from unittest.mock import Mock, patch, MagicMock

@pytest.fixture
def mock_credentials():
    """Mock OAuth credentials."""
    return {
        "claudeAiOauth": {
            "accessToken": "sk-ant-oat01-MOCK_ACCESS_TOKEN",
            "refreshToken": "sk-ant-ort01-MOCK_REFRESH_TOKEN",
            "expiresAt": 9999999999999,  # Far future
            "scopes": ["user:inference", "user:profile"],
            "subscriptionType": "max"
        }
    }

@pytest.fixture
def expired_credentials():
    """Mock expired OAuth credentials."""
    return {
        "claudeAiOauth": {
            "accessToken": "sk-ant-oat01-EXPIRED",
            "refreshToken": "sk-ant-ort01-VALID",
            "expiresAt": 1000000000000,  # Past
            "scopes": ["user:inference", "user:profile"],
            "subscriptionType": "max"
        }
    }
```

### Unit Test Categories

#### 1. Credentials Manager Tests (Story 2)
```python
# tests/unit/test_credentials_manager.py

def test_read_valid_credentials(mock_credentials):
    """Test reading valid credentials file."""
    with patch("pathlib.Path.read_text") as mock_read:
        mock_read.return_value = json.dumps(mock_credentials)
        creds = CredentialsManager.read()
        assert creds.access_token.startswith("sk-ant-oat01-")
        assert creds.is_valid()

def test_missing_credentials_file():
    """Test handling of missing credentials file."""
    with patch("pathlib.Path.exists", return_value=False):
        creds = CredentialsManager.read()
        assert creds is None

def test_token_expiration_check(expired_credentials):
    """Test token expiration detection."""
    creds = OAuthCredentials.from_dict(expired_credentials)
    assert creds.is_expired()
    assert not creds.is_valid()

def test_token_expiration_buffer():
    """Test 5-minute expiration buffer."""
    # Token expires in 4 minutes - should be considered expired
    expires_at = time.time() + (4 * 60)
    creds = OAuthCredentials(access_token="...", expires_at=expires_at)
    assert creds.is_expired()  # Due to 5-min buffer
```

#### 2. Configuration System Tests (Story 4)
```python
# tests/unit/test_auth_config.py

def test_env_var_override():
    """Test environment variable overrides SDK config."""
    os.environ["CLAUDE_AUTH_MODE"] = "api_key"
    config = AuthConfig(auth_mode=AuthMode.OAUTH)
    resolved = config.resolve()
    assert resolved.mode == AuthMode.API_KEY  # Env wins

def test_fallback_policy_strict():
    """Test strict mode disables fallback."""
    config = AuthConfig(
        auth_mode=AuthMode.OAUTH,
        auth_fallback=AuthFallbackPolicy.DISABLED
    )
    assert not config.allows_fallback()

def test_non_interactive_detection():
    """Test CI/CD auto-detection."""
    os.environ["CI"] = "true"
    config = AuthConfig()
    assert not config.is_interactive()

def test_priority_chain_oauth_first():
    """Test OAuth-first priority chain."""
    chain = AuthConfig().get_priority_chain()
    assert chain == ["oauth", "api_key"]

def test_priority_chain_api_key_mode():
    """Test API key mode skips OAuth."""
    config = AuthConfig(auth_mode=AuthMode.API_KEY)
    chain = config.get_priority_chain()
    assert chain == ["api_key"]
```

#### 3. State Machine Tests (Story 5.1)
```python
# tests/unit/test_auth_state_machine.py

def test_oauth_valid_state():
    """Test OAuth valid state."""
    state = AuthStateMachine(valid_oauth_creds=True)
    assert state.current == AuthState.OAUTH_VALID

def test_oauth_refresh_needed():
    """Test transition to refresh needed."""
    state = AuthStateMachine()
    state.on_token_expired()
    assert state.current == AuthState.OAUTH_REFRESH_NEEDED

def test_oauth_login_needed():
    """Test transition to login needed."""
    state = AuthStateMachine()
    state.on_refresh_failed()
    assert state.current == AuthState.OAUTH_LOGIN_NEEDED

def test_fallback_to_api_key():
    """Test fallback transition."""
    state = AuthStateMachine(fallback_enabled=True)
    state.on_oauth_failed()
    assert state.current == AuthState.API_KEY_MODE

def test_strict_mode_error():
    """Test strict mode prevents fallback."""
    state = AuthStateMachine(fallback_enabled=False)
    with pytest.raises(AuthenticationError):
        state.on_oauth_failed()
```

#### 4. Browser OAuth Flow Tests (Story 3.2)
```python
# tests/unit/test_browser_oauth.py

@pytest.mark.asyncio
async def test_callback_server_starts():
    """Test local callback server starts."""
    flow = BrowserOAuthFlow()
    async with flow.start_callback_server() as url:
        assert url.startswith("http://localhost:")

@pytest.mark.asyncio
async def test_authorization_url_generation():
    """Test OAuth authorization URL."""
    flow = BrowserOAuthFlow()
    url = flow.get_authorization_url()
    assert "anthropic.com" in url
    assert "response_type=code" in url
    assert "scope=user:inference" in url

@pytest.mark.asyncio
async def test_token_exchange(mock_http_response):
    """Test exchanging auth code for tokens."""
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value = mock_http_response({
            "access_token": "sk-ant-oat01-NEW",
            "refresh_token": "sk-ant-ort01-NEW",
            "expires_in": 3600
        })
        flow = BrowserOAuthFlow()
        tokens = await flow.exchange_code("AUTH_CODE_123")
        assert tokens.access_token.startswith("sk-ant-oat01-")
```

### Unit Test Metrics

**Target Coverage**: 90%+
**Test Count**: ~100 tests
**Runtime**: <1 minute
**CI/CD**: Run on every commit

## Tier 2: Integration Tests

### Test Framework
```python
# pytest with real API calls
import pytest
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

@pytest.fixture(scope="session")
def test_oauth_credentials():
    """Real OAuth credentials for test account."""
    # Use dedicated test account
    return CredentialsManager.read()  # ~/.claude/.credentials.json

@pytest.fixture(scope="session")
def test_api_key():
    """Real API key for fallback tests."""
    return os.environ.get("ANTHROPIC_API_KEY_TEST")
```

### Integration Test Categories

#### 1. OAuth Flow End-to-End (Story 7.2)
```python
# tests/integration/test_oauth_flow.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_oauth_request_with_valid_tokens():
    """Test real API request using OAuth tokens."""
    options = ClaudeAgentOptions(
        auth_mode=AuthMode.OAUTH,
        auth_fallback=AuthFallbackPolicy.DISABLED
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("What is 2 + 2?")
        async for message in client.receive_response():
            assert message is not None

    # Verify used OAuth (check logs)
    assert "Using OAuth authentication" in captured_logs

@pytest.mark.integration
@pytest.mark.asyncio
async def test_browser_oauth_flow():
    """Test complete browser OAuth flow."""
    # Delete credentials to force new login
    credentials_path.unlink(missing_ok=True)

    options = ClaudeAgentOptions(auth_mode=AuthMode.OAUTH)

    # This should trigger browser login
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Hello")
        async for message in client.receive_response():
            pass

    # Verify credentials were created
    assert credentials_path.exists()
    creds = CredentialsManager.read()
    assert creds.is_valid()
```

#### 2. Token Refresh Tests (Story 7.4)
```python
# tests/integration/test_token_refresh.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_auto_refresh_expired_token():
    """Test automatic token refresh."""
    # Artificially expire access token
    creds = CredentialsManager.read()
    creds.expires_at = time.time() - 100  # Expired
    CredentialsManager.save(creds)

    options = ClaudeAgentOptions(auth_mode=AuthMode.OAUTH)

    async with ClaudeSDKClient(options=options) as client:
        # Should auto-refresh before request
        await client.query("Test")
        async for message in client.receive_response():
            pass

    # Verify token was refreshed
    new_creds = CredentialsManager.read()
    assert new_creds.access_token != creds.access_token
    assert new_creds.is_valid()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_refresh_prevention():
    """Test multiple requests don't cause duplicate refreshes."""
    # Expire token
    creds = CredentialsManager.read()
    creds.expires_at = time.time() - 100
    CredentialsManager.save(creds)

    # Make 10 concurrent requests
    async with ClaudeSDKClient() as client:
        tasks = [client.query(f"Request {i}") for i in range(10)]
        await asyncio.gather(*tasks)

    # Verify only ONE refresh occurred (check logs)
    refresh_count = captured_logs.count("Refreshing OAuth token")
    assert refresh_count == 1
```

#### 3. Fallback Behavior Tests (Story 7.3)
```python
# tests/integration/test_fallback.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_oauth_fails_fallback_to_api_key():
    """Test fallback to API key when OAuth fails."""
    # Corrupt OAuth credentials
    credentials_path.write_text('{"invalid": "json"}')

    # Set API key
    os.environ["ANTHROPIC_API_KEY"] = test_api_key()

    options = ClaudeAgentOptions(
        auth_mode=AuthMode.AUTO,
        auth_fallback=AuthFallbackPolicy.ENABLED
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Test")
        async for message in client.receive_response():
            pass

    # Verify fallback occurred
    assert "Falling back to API key" in captured_logs

    # Verify used API key (check billing later)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_strict_mode_no_fallback():
    """Test strict mode errors instead of falling back."""
    # Corrupt OAuth credentials
    credentials_path.write_text('{"invalid": "json"}')

    # Set API key (should NOT be used)
    os.environ["ANTHROPIC_API_KEY"] = test_api_key()

    options = ClaudeAgentOptions(
        auth_mode=AuthMode.OAUTH,
        auth_fallback=AuthFallbackPolicy.DISABLED
    )

    with pytest.raises(AuthenticationError):
        async with ClaudeSDKClient(options=options) as client:
            await client.query("Test")
```

### Integration Test Metrics

**Target Coverage**: Key user journeys
**Test Count**: ~20 tests
**Runtime**: ~5 minutes (real API calls)
**CI/CD**: Run on PR merge, scheduled nightly
**Cost**: ~$0.50 per run (API usage)

## Tier 3: Manual Verification

### Manual Test Checklist

#### Pre-Test Setup
- [ ] Create test Claude Max account
- [ ] Install Claude CLI: `npm install -g @anthropic-ai/claude-code`
- [ ] Clear existing credentials: `rm ~/.claude/.credentials.json`
- [ ] Set up test environment variables

#### Scenario 1: First-Time OAuth Login
```bash
# Clean state
rm ~/.claude/.credentials.json
unset ANTHROPIC_API_KEY

# Run SDK
python examples/oauth_demo.py

# Expected:
# - Browser opens automatically
# - Login page loads
# - After login, returns to terminal
# - Request succeeds
# - Check: ~/.claude/.credentials.json exists
```

#### Scenario 2: Token Auto-Refresh
```bash
# Expire access token manually
python -c "
import json, time
from pathlib import Path
p = Path.home() / '.claude/.credentials.json'
data = json.loads(p.read_text())
data['claudeAiOauth']['expiresAt'] = int(time.time() * 1000) - 1000
p.write_text(json.dumps(data, indent=2))
"

# Run SDK
python examples/oauth_demo.py

# Expected:
# - No browser opens (refresh works silently)
# - Request succeeds
# - Check logs: "Refreshing OAuth token"
# - Check: expiresAt updated in credentials file
```

#### Scenario 3: Fallback to API Key
```bash
# Corrupt OAuth, set API key
echo '{"invalid"}' > ~/.claude/.credentials.json
export ANTHROPIC_API_KEY=sk-ant-api...

# Run SDK with fallback enabled
python examples/oauth_demo.py

# Expected:
# - Warning: "Falling back to API key mode"
# - Request succeeds
# - Check dashboard: usage on API credits, NOT subscription
```

#### Scenario 4: Strict Mode (No Fallback)
```bash
# Corrupt OAuth, set API key
echo '{"invalid"}' > ~/.claude/.credentials.json
export ANTHROPIC_API_KEY=sk-ant-api...
export CLAUDE_AUTH_STRICT=true

# Run SDK
python examples/oauth_demo.py

# Expected:
# - ERROR: "OAuth authentication failed (strict mode)"
# - Script exits with error
# - API key NOT used
```

#### Scenario 5: Non-Interactive (CI/CD)
```bash
# Set up valid OAuth credentials
# Set non-interactive flag
export CLAUDE_AUTH_INTERACTIVE=false

# Run SDK
python examples/oauth_demo.py

# Expected:
# - Uses existing OAuth credentials
# - NO browser opens
# - Request succeeds

# Now expire refresh token
# (manually set expiresAt very old)

# Run SDK again
python examples/oauth_demo.py

# Expected:
# - ERROR or fallback to API key
# - NO browser opens (non-interactive)
```

#### Scenario 6: Subscription Usage Verification
```bash
# Use OAuth mode
python examples/oauth_demo.py

# Then check:
# 1. Visit https://claude.ai/settings/usage
# 2. Verify "Claude Max" usage increased
# 3. Verify NO API credits deducted
```

### Cross-Platform Testing

Test on all three platforms:
- [ ] Windows 10/11
- [ ] macOS (Intel + ARM)
- [ ] Linux (Ubuntu 22.04)

For each platform, verify:
- [ ] Browser OAuth flow works
- [ ] Credentials file path correct
- [ ] Environment variables work
- [ ] Subprocess communication works

### Manual Verification Metrics

**Test Scenarios**: ~10 scenarios
**Time**: ~30 minutes
**Frequency**: Before each release
**Platforms**: Windows, macOS, Linux

## Test Environments

### Development Environment
```bash
# Local testing
python -m pytest tests/unit/  # Unit tests
python -m pytest tests/integration/ --runslow  # Integration tests
```

### CI/CD Environment (GitHub Actions)
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit/ -v

  integration-tests:
    runs-on: ubuntu-latest
    # Only on main branch (to save costs)
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: pytest tests/integration/ -v
        env:
          ANTHROPIC_API_KEY_TEST: ${{ secrets.TEST_API_KEY }}
          # Use credentials from secrets
```

### Test Data Management

#### Mock Credentials
```python
# tests/fixtures/mock_credentials.json
{
  "claudeAiOauth": {
    "accessToken": "sk-ant-oat01-MOCK_FOR_TESTING_DO_NOT_USE",
    "refreshToken": "sk-ant-ort01-MOCK_FOR_TESTING_DO_NOT_USE",
    "expiresAt": 9999999999999,
    "scopes": ["user:inference", "user:profile"],
    "subscriptionType": "max"
  }
}
```

#### Test Account
- Dedicated test Claude Max account
- Credentials stored in GitHub Secrets
- Monthly cost: ~$200 (Max subscription)

## Success Criteria

### Unit Tests
- ✅ 90%+ code coverage
- ✅ All tests pass in <1 minute
- ✅ No external dependencies

### Integration Tests
- ✅ All OAuth flows work end-to-end
- ✅ Token refresh works automatically
- ✅ Fallback scenarios tested
- ✅ Real API calls succeed

### Manual Verification
- ✅ Browser OAuth flow smooth UX
- ✅ Subscription usage verified (not API credits)
- ✅ Works on all platforms
- ✅ Error messages clear and helpful

## Test Maintenance

### Adding New Tests
1. Write unit test first (TDD)
2. Ensure it passes
3. Add integration test if needed
4. Update manual checklist if UX changes

### Updating Tests
- When adding new auth modes: update all 3 tiers
- When changing config: update unit + integration tests
- When changing UX: update manual verification

### Test Review
- All PRs must include tests
- CI must pass before merge
- Manual verification before release
