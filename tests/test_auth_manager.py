"""Tests for authentication manager."""

import os
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from claude_agent_sdk._internal.auth_manager import (
    AuthenticationManager,
    AuthenticationResult,
    AuthState,
    get_authenticated_headers,
)
from claude_agent_sdk._internal.oauth_credentials import OAuthCredentials


@pytest.fixture
def valid_oauth_creds():
    """Create valid OAuth credentials."""
    # Token expires in 1 hour
    expires_at = int((datetime.now(timezone.utc).timestamp() + 3600) * 1000)
    return OAuthCredentials(
        access_token="sk-ant-oat01-test-access-token",
        refresh_token="sk-ant-ort01-test-refresh-token",
        expires_at=expires_at,
        scopes=["user:inference", "user:profile"],
        subscription="max",
    )


@pytest.fixture
def expired_oauth_creds():
    """Create expired OAuth credentials."""
    # Token expired 1 hour ago
    expires_at = int((datetime.now(timezone.utc).timestamp() - 3600) * 1000)
    return OAuthCredentials(
        access_token="sk-ant-oat01-test-access-token",
        refresh_token="sk-ant-ort01-test-refresh-token",
        expires_at=expires_at,
        scopes=["user:inference", "user:profile"],
        subscription="max",
    )


@pytest.fixture
def clear_env():
    """Clear auth-related environment variables."""
    env_vars = [
        "ANTHROPIC_API_KEY",
        "CLAUDE_AUTH_MODE",
        "CLAUDE_AUTH_FALLBACK",
        "CLAUDE_AUTH_STRICT",
        "CLAUDE_AUTH_INTERACTIVE",
    ]
    original_values = {}
    for var in env_vars:
        original_values[var] = os.environ.pop(var, None)

    yield

    # Restore original values
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value


class TestAuthState:
    """Test AuthState enum."""

    def test_auth_state_values(self):
        """Test auth state enum values."""
        assert AuthState.API_KEY_MODE.value == "api_key_mode"
        assert AuthState.OAUTH_VALID.value == "oauth_valid"
        assert AuthState.OAUTH_REFRESH_NEEDED.value == "oauth_refresh_needed"
        assert AuthState.OAUTH_LOGIN_NEEDED.value == "oauth_login_needed"
        assert AuthState.AUTH_FAILED.value == "auth_failed"


class TestAuthenticationResult:
    """Test AuthenticationResult."""

    def test_oauth_valid_result(self, valid_oauth_creds):
        """Test result for valid OAuth."""
        result = AuthenticationResult(
            state=AuthState.OAUTH_VALID, credentials=valid_oauth_creds
        )

        assert result.is_oauth
        assert not result.is_api_key
        assert result.is_ready
        assert result.credentials == valid_oauth_creds

    def test_api_key_result(self):
        """Test result for API key mode."""
        result = AuthenticationResult(
            state=AuthState.API_KEY_MODE, api_key="test-api-key"
        )

        assert not result.is_oauth
        assert result.is_api_key
        assert result.is_ready
        assert result.api_key == "test-api-key"

    def test_auth_failed_result(self):
        """Test result for auth failed."""
        result = AuthenticationResult(state=AuthState.AUTH_FAILED, error="Test error")

        assert not result.is_oauth
        assert not result.is_api_key
        assert not result.is_ready
        assert result.error == "Test error"

    def test_get_auth_header_oauth(self, valid_oauth_creds):
        """Test getting OAuth auth header."""
        result = AuthenticationResult(
            state=AuthState.OAUTH_VALID, credentials=valid_oauth_creds
        )

        headers = result.get_auth_header()
        assert headers == {"Authorization": f"Bearer {valid_oauth_creds.access_token}"}

    def test_get_auth_header_api_key(self):
        """Test getting API key auth header."""
        result = AuthenticationResult(state=AuthState.API_KEY_MODE, api_key="test-key")

        headers = result.get_auth_header()
        assert headers == {"x-api-key": "test-key"}

    def test_get_auth_header_not_ready(self):
        """Test error when getting header from non-ready state."""
        result = AuthenticationResult(state=AuthState.AUTH_FAILED)

        with pytest.raises(RuntimeError, match="Authentication not ready"):
            result.get_auth_header()


class TestAuthenticationManager:
    """Test AuthenticationManager."""

    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_detect_state_oauth_valid(
        self, mock_read_creds, valid_oauth_creds, clear_env
    ):
        """Test detecting OAUTH_VALID state."""
        mock_read_creds.return_value = valid_oauth_creds

        manager = AuthenticationManager()
        state = manager.detect_auth_state()

        assert state == AuthState.OAUTH_VALID
        assert manager._current_credentials == valid_oauth_creds

    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_detect_state_oauth_refresh_needed(
        self, mock_read_creds, expired_oauth_creds, clear_env
    ):
        """Test detecting OAUTH_REFRESH_NEEDED state."""
        mock_read_creds.return_value = expired_oauth_creds

        manager = AuthenticationManager()
        state = manager.detect_auth_state()

        assert state == AuthState.OAUTH_REFRESH_NEEDED
        assert manager._current_credentials == expired_oauth_creds

    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_detect_state_oauth_login_needed(self, mock_read_creds, clear_env):
        """Test detecting OAUTH_LOGIN_NEEDED state."""
        mock_read_creds.side_effect = Exception("No credentials")

        manager = AuthenticationManager()
        state = manager.detect_auth_state()

        assert state == AuthState.OAUTH_LOGIN_NEEDED

    def test_detect_state_api_key_mode(self, clear_env):
        """Test detecting API_KEY_MODE state."""
        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
        os.environ["CLAUDE_AUTH_MODE"] = "api_key"

        manager = AuthenticationManager()
        state = manager.detect_auth_state()

        assert state == AuthState.API_KEY_MODE

    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_detect_state_fallback_to_api_key(self, mock_read_creds, clear_env):
        """Test fallback to API key when OAuth not available."""

        mock_read_creds.side_effect = Exception("No credentials")
        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
        os.environ["CLAUDE_AUTH_MODE"] = "auto"
        os.environ["CLAUDE_AUTH_FALLBACK"] = "true"

        manager = AuthenticationManager()

        with pytest.warns(UserWarning, match="falling back to API key"):
            state = manager.detect_auth_state()

        assert state == AuthState.API_KEY_MODE

    @patch("claude_agent_sdk._internal.auth_manager.refresh_oauth_token")
    def test_handle_oauth_refresh_success(
        self, mock_refresh, valid_oauth_creds, clear_env
    ):
        """Test successful OAuth token refresh."""
        mock_refresh.return_value = valid_oauth_creds

        manager = AuthenticationManager()
        result = manager.handle_oauth_refresh()

        assert result.state == AuthState.OAUTH_VALID
        assert result.credentials == valid_oauth_creds
        assert manager._current_state == AuthState.OAUTH_VALID

    @patch("claude_agent_sdk._internal.auth_manager.refresh_oauth_token")
    def test_handle_oauth_refresh_failure_with_fallback(self, mock_refresh, clear_env):
        """Test OAuth refresh failure with API key fallback."""
        mock_refresh.return_value = None
        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
        os.environ["CLAUDE_AUTH_FALLBACK"] = "true"

        manager = AuthenticationManager()

        with pytest.warns(UserWarning, match="falling back to API key"):
            result = manager.handle_oauth_refresh()

        assert result.state == AuthState.API_KEY_MODE
        assert result.api_key == "test-api-key"

    @patch("claude_agent_sdk._internal.auth_manager.refresh_oauth_token")
    def test_handle_oauth_refresh_failure_strict_mode(self, mock_refresh, clear_env):
        """Test OAuth refresh failure in strict mode."""
        mock_refresh.return_value = None
        os.environ["CLAUDE_AUTH_STRICT"] = "true"

        manager = AuthenticationManager()
        result = manager.handle_oauth_refresh()

        assert result.state == AuthState.AUTH_FAILED
        assert result.error is not None
        assert "refresh failed" in result.error.lower()

    @patch("claude_agent_sdk._internal.auth_manager.trigger_oauth_login")
    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_handle_oauth_login_success(
        self, mock_read_creds, mock_login, valid_oauth_creds, clear_env
    ):
        """Test successful OAuth login."""
        mock_login.return_value = True
        mock_read_creds.return_value = valid_oauth_creds
        os.environ["CLAUDE_AUTH_INTERACTIVE"] = "true"

        manager = AuthenticationManager()
        result = manager.handle_oauth_login()

        assert result.state == AuthState.OAUTH_VALID
        assert result.credentials == valid_oauth_creds

    @patch("claude_agent_sdk._internal.auth_manager.trigger_oauth_login")
    def test_handle_oauth_login_failure_with_fallback(self, mock_login, clear_env):
        """Test OAuth login failure with API key fallback."""
        mock_login.return_value = False
        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
        os.environ["CLAUDE_AUTH_FALLBACK"] = "true"
        os.environ["CLAUDE_AUTH_INTERACTIVE"] = "true"

        manager = AuthenticationManager()

        with pytest.warns(UserWarning, match="falling back to API key"):
            result = manager.handle_oauth_login()

        assert result.state == AuthState.API_KEY_MODE
        assert result.api_key == "test-api-key"

    def test_handle_oauth_login_non_interactive_with_fallback(self, clear_env):
        """Test OAuth login in non-interactive mode with fallback."""
        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
        os.environ["CLAUDE_AUTH_FALLBACK"] = "true"
        os.environ["CLAUDE_AUTH_INTERACTIVE"] = "false"

        manager = AuthenticationManager()

        with pytest.warns(UserWarning, match="non-interactive"):
            result = manager.handle_oauth_login()

        assert result.state == AuthState.API_KEY_MODE
        assert result.api_key == "test-api-key"

    def test_handle_oauth_login_non_interactive_strict(self, clear_env):
        """Test OAuth login in non-interactive strict mode."""
        os.environ["CLAUDE_AUTH_STRICT"] = "true"
        os.environ["CLAUDE_AUTH_INTERACTIVE"] = "false"

        manager = AuthenticationManager()
        result = manager.handle_oauth_login()

        assert result.state == AuthState.AUTH_FAILED
        assert result.error is not None
        assert "non-interactive" in result.error.lower()

    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_ensure_authenticated_oauth_valid(
        self, mock_read_creds, valid_oauth_creds, clear_env
    ):
        """Test ensure_authenticated with valid OAuth."""

        mock_read_creds.return_value = valid_oauth_creds

        manager = AuthenticationManager()
        result = manager.ensure_authenticated()

        assert result.state == AuthState.OAUTH_VALID
        assert result.is_ready
        headers = result.get_auth_header()
        assert "Authorization" in headers

    def test_ensure_authenticated_api_key(self, clear_env):
        """Test ensure_authenticated with API key."""
        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
        os.environ["CLAUDE_AUTH_MODE"] = "api_key"

        manager = AuthenticationManager()
        result = manager.ensure_authenticated()

        assert result.state == AuthState.API_KEY_MODE
        assert result.is_ready
        headers = result.get_auth_header()
        assert headers == {"x-api-key": "test-api-key"}

    @patch("claude_agent_sdk._internal.auth_manager.refresh_oauth_token")
    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_ensure_authenticated_with_refresh(
        self,
        mock_read_creds,
        mock_refresh,
        expired_oauth_creds,
        valid_oauth_creds,
        clear_env,
    ):
        """Test ensure_authenticated triggers refresh."""

        mock_read_creds.return_value = expired_oauth_creds
        mock_refresh.return_value = valid_oauth_creds

        manager = AuthenticationManager()
        result = manager.ensure_authenticated()

        assert result.state == AuthState.OAUTH_VALID
        assert result.credentials == valid_oauth_creds
        mock_refresh.assert_called_once()

    @patch("claude_agent_sdk._internal.auth_manager.trigger_oauth_login")
    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_ensure_authenticated_with_login(
        self,
        mock_read_creds,
        mock_login,
        valid_oauth_creds,
        clear_env,
    ):
        """Test ensure_authenticated triggers login."""

        # First call returns None (detect state), second call returns valid creds (after login)
        mock_read_creds.side_effect = [None, valid_oauth_creds]
        mock_login.return_value = True
        os.environ["CLAUDE_AUTH_INTERACTIVE"] = "true"

        manager = AuthenticationManager()
        result = manager.ensure_authenticated()

        assert result.state == AuthState.OAUTH_VALID
        assert result.credentials == valid_oauth_creds
        mock_login.assert_called_once()

    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_ensure_authenticated_strict_mode_failure(self, mock_read_creds, clear_env):
        """Test ensure_authenticated raises in strict mode."""

        mock_read_creds.side_effect = Exception("No credentials")
        os.environ["CLAUDE_AUTH_STRICT"] = "true"
        os.environ["CLAUDE_AUTH_INTERACTIVE"] = "false"

        manager = AuthenticationManager()

        with pytest.raises(RuntimeError, match="OAuth login required"):
            manager.ensure_authenticated()

    def test_reset_state(self, clear_env):
        """Test reset_state clears cached state."""
        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"

        manager = AuthenticationManager()
        manager._current_state = AuthState.API_KEY_MODE

        assert manager.get_current_state() == AuthState.API_KEY_MODE

        manager.reset_state()

        assert manager.get_current_state() is None
        assert manager._current_credentials is None

    def test_get_current_state(self, clear_env):
        """Test get_current_state."""
        manager = AuthenticationManager()

        assert manager.get_current_state() is None

        manager._current_state = AuthState.OAUTH_VALID

        assert manager.get_current_state() == AuthState.OAUTH_VALID


class TestGetAuthenticatedHeaders:
    """Test get_authenticated_headers convenience function."""

    def test_get_headers_api_key(self, clear_env):
        """Test getting headers with API key."""
        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
        os.environ["CLAUDE_AUTH_MODE"] = "api_key"

        headers = get_authenticated_headers()

        assert headers == {"x-api-key": "test-api-key"}

    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_get_headers_oauth(self, mock_read_creds, valid_oauth_creds, clear_env):
        """Test getting headers with OAuth."""

        mock_read_creds.return_value = valid_oauth_creds

        headers = get_authenticated_headers()

        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")

    @patch("claude_agent_sdk._internal.auth_manager.read_credentials")
    def test_get_headers_failure(self, mock_read_creds, clear_env):
        """Test get_authenticated_headers raises on failure."""

        mock_read_creds.side_effect = Exception("No credentials")
        os.environ["CLAUDE_AUTH_STRICT"] = "true"
        os.environ["CLAUDE_AUTH_INTERACTIVE"] = "false"

        with pytest.raises(RuntimeError):
            get_authenticated_headers()
