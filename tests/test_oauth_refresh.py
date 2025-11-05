"""Tests for OAuth token refresh module."""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from claude_agent_sdk._internal.oauth_credentials import OAuthCredentials
from claude_agent_sdk._internal.oauth_refresh import (
    ensure_token_fresh,
    get_token_ttl_seconds,
    is_refresh_needed,
    refresh_oauth_token,
    should_refresh_token,
    trigger_proactive_refresh,
)


@pytest.fixture
def mock_valid_credentials():
    """Mock valid OAuth credentials (expires in 1 hour)."""
    return OAuthCredentials(
        access_token="sk-ant-oat01-valid-token",
        refresh_token="sk-ant-ort01-valid-refresh",
        expires_at=int(
            (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp() * 1000
        ),
        scopes=["user:inference", "user:profile"],
        subscription="max",
    )


@pytest.fixture
def mock_expiring_soon_credentials():
    """Mock credentials expiring soon (in 2 minutes)."""
    return OAuthCredentials(
        access_token="sk-ant-oat01-expiring-token",
        refresh_token="sk-ant-ort01-expiring-refresh",
        expires_at=int(
            (datetime.now(timezone.utc) + timedelta(minutes=2)).timestamp() * 1000
        ),
        scopes=["user:inference", "user:profile"],
        subscription="max",
    )


@pytest.fixture
def mock_expired_credentials():
    """Mock expired OAuth credentials."""
    return OAuthCredentials(
        access_token="sk-ant-oat01-expired-token",
        refresh_token="sk-ant-ort01-expired-refresh",
        expires_at=int(
            (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp() * 1000
        ),
        scopes=["user:inference", "user:profile"],
        subscription="max",
    )


class TestRefreshOAuthToken:
    """Tests for refresh_oauth_token function."""

    @patch("claude_agent_sdk._internal.oauth_refresh.read_credentials")
    def test_no_credentials_returns_none(self, mock_read):
        """Test returns None when no credentials exist."""
        mock_read.return_value = None

        result = refresh_oauth_token()

        assert result is None

    @patch("claude_agent_sdk._internal.oauth_refresh.read_credentials")
    def test_already_fresh_returns_immediately(self, mock_read, mock_valid_credentials):
        """Test returns immediately when token is already fresh."""
        mock_read.return_value = mock_valid_credentials

        result = refresh_oauth_token()

        assert result == mock_valid_credentials
        # Should not attempt subprocess
        mock_read.assert_called_once()

    @patch("claude_agent_sdk._internal.oauth_refresh.subprocess.run")
    @patch("claude_agent_sdk._internal.oauth_refresh.read_credentials")
    @patch("claude_agent_sdk._internal.oauth_refresh.time.sleep")
    def test_auto_refresh_success(
        self,
        mock_sleep,
        mock_read,
        mock_subprocess,
        mock_expired_credentials,
        mock_valid_credentials,
    ):
        """Test successful auto-refresh via Claude CLI."""
        # First call: expired
        # Second call (after subprocess): refreshed
        mock_read.side_effect = [mock_expired_credentials, mock_valid_credentials]
        mock_subprocess.return_value = Mock(returncode=0)

        result = refresh_oauth_token(interactive=False)

        assert result == mock_valid_credentials
        mock_subprocess.assert_called_once()
        mock_sleep.assert_called_once()

    @patch("claude_agent_sdk._internal.oauth_refresh.subprocess.run")
    @patch("claude_agent_sdk._internal.oauth_refresh.read_credentials")
    @patch("claude_agent_sdk._internal.oauth_refresh.time.sleep")
    def test_auto_refresh_failed(
        self,
        mock_sleep,
        mock_read,
        mock_subprocess,
        mock_expired_credentials,
    ):
        """Test failed auto-refresh (credentials still expired)."""
        mock_read.return_value = mock_expired_credentials
        mock_subprocess.return_value = Mock(returncode=0)

        result = refresh_oauth_token(interactive=False)

        assert result is None

    @patch("claude_agent_sdk._internal.oauth_login.trigger_oauth_login")
    @patch("claude_agent_sdk._internal.oauth_refresh.subprocess.run")
    @patch("claude_agent_sdk._internal.oauth_refresh.read_credentials")
    @patch("claude_agent_sdk._internal.oauth_refresh.time.sleep")
    def test_fallback_to_relogin_success(
        self,
        mock_sleep,
        mock_read,
        mock_subprocess,
        mock_trigger,
        mock_expired_credentials,
        mock_valid_credentials,
    ):
        """Test fallback to full re-login when auto-refresh fails."""
        # First call: expired
        # Second call (after subprocess): still expired
        # Third call (after re-login): refreshed
        mock_read.side_effect = [
            mock_expired_credentials,
            mock_expired_credentials,
            mock_valid_credentials,
        ]
        mock_subprocess.return_value = Mock(returncode=0)
        mock_trigger.return_value = True

        result = refresh_oauth_token(interactive=True)

        assert result == mock_valid_credentials
        mock_trigger.assert_called_once_with(interactive=True)

    @patch("claude_agent_sdk._internal.oauth_refresh.subprocess.run")
    @patch("claude_agent_sdk._internal.oauth_refresh.read_credentials")
    @patch("claude_agent_sdk._internal.oauth_refresh.time.sleep")
    def test_subprocess_error(
        self, mock_sleep, mock_read, mock_subprocess, mock_expired_credentials
    ):
        """Test handling of subprocess errors."""
        mock_read.return_value = mock_expired_credentials
        mock_subprocess.side_effect = FileNotFoundError()

        result = refresh_oauth_token(interactive=False)

        assert result is None


class TestEnsureTokenFresh:
    """Tests for ensure_token_fresh function."""

    def test_already_fresh(self, mock_valid_credentials):
        """Test when token is already fresh."""
        result = ensure_token_fresh(mock_valid_credentials)

        assert result == mock_valid_credentials

    @patch("claude_agent_sdk._internal.oauth_refresh.refresh_oauth_token")
    def test_refresh_success(
        self, mock_refresh, mock_expired_credentials, mock_valid_credentials
    ):
        """Test successful refresh."""
        mock_refresh.return_value = mock_valid_credentials

        result = ensure_token_fresh(mock_expired_credentials)

        assert result == mock_valid_credentials
        mock_refresh.assert_called_once_with(interactive=True)

    @patch("claude_agent_sdk._internal.oauth_refresh.refresh_oauth_token")
    def test_refresh_failed(self, mock_refresh, mock_expired_credentials):
        """Test error when refresh fails."""
        mock_refresh.return_value = None

        with pytest.raises(RuntimeError, match="could not be refreshed"):
            ensure_token_fresh(mock_expired_credentials)


class TestIsRefreshNeeded:
    """Tests for is_refresh_needed function."""

    def test_valid_token_no_refresh_needed(self, mock_valid_credentials):
        """Test that valid token doesn't need refresh."""
        result = is_refresh_needed(mock_valid_credentials)

        assert result is False

    def test_expired_token_needs_refresh(self, mock_expired_credentials):
        """Test that expired token needs refresh."""
        result = is_refresh_needed(mock_expired_credentials)

        assert result is True

    def test_expiring_soon_needs_refresh(self, mock_expiring_soon_credentials):
        """Test that token expiring soon needs refresh."""
        # Credentials expire in 2 minutes, default buffer is 5 minutes
        result = is_refresh_needed(mock_expiring_soon_credentials, buffer_seconds=300)

        assert result is True


class TestTriggerProactiveRefresh:
    """Tests for trigger_proactive_refresh function."""

    def test_no_refresh_needed(self, mock_valid_credentials):
        """Test when no refresh is needed."""
        result = trigger_proactive_refresh(mock_valid_credentials)

        assert result == mock_valid_credentials

    @patch("claude_agent_sdk._internal.oauth_refresh.refresh_oauth_token")
    def test_refresh_triggered_success(
        self, mock_refresh, mock_expired_credentials, mock_valid_credentials
    ):
        """Test successful proactive refresh."""
        mock_refresh.return_value = mock_valid_credentials

        result = trigger_proactive_refresh(mock_expired_credentials)

        assert result == mock_valid_credentials
        # Should use non-interactive mode
        mock_refresh.assert_called_once_with(interactive=False)

    @patch("claude_agent_sdk._internal.oauth_refresh.refresh_oauth_token")
    def test_refresh_triggered_failed(self, mock_refresh, mock_expired_credentials):
        """Test failed proactive refresh."""
        mock_refresh.return_value = None

        result = trigger_proactive_refresh(mock_expired_credentials)

        assert result is None


class TestGetTokenTTLSeconds:
    """Tests for get_token_ttl_seconds function."""

    def test_valid_token_positive_ttl(self, mock_valid_credentials):
        """Test TTL calculation for valid token."""
        ttl = get_token_ttl_seconds(mock_valid_credentials)

        # Should be approximately 1 hour (3600 seconds)
        assert 3500 < ttl < 3700

    def test_expired_token_negative_ttl(self, mock_expired_credentials):
        """Test TTL calculation for expired token."""
        ttl = get_token_ttl_seconds(mock_expired_credentials)

        # Should be negative (approximately -1 hour)
        assert -3700 < ttl < -3500

    def test_expiring_soon_small_ttl(self, mock_expiring_soon_credentials):
        """Test TTL calculation for token expiring soon."""
        ttl = get_token_ttl_seconds(mock_expiring_soon_credentials)

        # Should be approximately 2 minutes (120 seconds)
        assert 100 < ttl < 140


class TestShouldRefreshToken:
    """Tests for should_refresh_token function."""

    def test_valid_token_no_refresh(self, mock_valid_credentials):
        """Test that valid token doesn't need refresh."""
        should_refresh, reason = should_refresh_token(mock_valid_credentials)

        assert should_refresh is False
        assert "valid for" in reason.lower()

    def test_expired_token_should_refresh(self, mock_expired_credentials):
        """Test that expired token should be refreshed."""
        should_refresh, reason = should_refresh_token(mock_expired_credentials)

        assert should_refresh is True
        assert "expired" in reason.lower()

    def test_expiring_soon_should_refresh(self, mock_expiring_soon_credentials):
        """Test that token expiring soon should be refreshed."""
        should_refresh, reason = should_refresh_token(
            mock_expiring_soon_credentials, min_ttl_seconds=300
        )

        assert should_refresh is True
        assert "expires in" in reason.lower() and "buffer" in reason.lower()

    def test_custom_buffer(self, mock_valid_credentials):
        """Test custom buffer time."""
        # Token expires in 1 hour, but require 2 hour buffer
        should_refresh, reason = should_refresh_token(
            mock_valid_credentials, min_ttl_seconds=7200
        )

        assert should_refresh is True
        assert "buffer" in reason.lower()

    def test_reason_contains_ttl(self, mock_valid_credentials):
        """Test that reason contains TTL information."""
        should_refresh, reason = should_refresh_token(mock_valid_credentials)

        # Reason should contain seconds
        assert "seconds" in reason.lower()
        # Should have a number
        assert any(char.isdigit() for char in reason)


class TestTokenRefreshIntegration:
    """Integration tests for token refresh workflow."""

    @patch("claude_agent_sdk._internal.oauth_refresh.subprocess.run")
    @patch("claude_agent_sdk._internal.oauth_refresh.read_credentials")
    @patch("claude_agent_sdk._internal.oauth_refresh.time.sleep")
    def test_complete_refresh_workflow(
        self,
        mock_sleep,
        mock_read,
        mock_subprocess,
        mock_expired_credentials,
        mock_valid_credentials,
    ):
        """Test complete refresh workflow from detection to completion."""
        # Setup
        mock_read.side_effect = [mock_expired_credentials, mock_valid_credentials]
        mock_subprocess.return_value = Mock(returncode=0)

        # Check if refresh needed
        assert is_refresh_needed(mock_expired_credentials) is True

        # Trigger refresh
        result = refresh_oauth_token(interactive=False)

        # Verify
        assert result == mock_valid_credentials
        assert is_refresh_needed(result) is False

    @patch("claude_agent_sdk._internal.oauth_refresh.refresh_oauth_token")
    def test_ensure_fresh_workflow(
        self, mock_refresh, mock_expiring_soon_credentials, mock_valid_credentials
    ):
        """Test ensure_token_fresh workflow."""
        mock_refresh.return_value = mock_valid_credentials

        # Token expiring soon
        creds = mock_expiring_soon_credentials
        assert is_refresh_needed(creds) is True

        # Ensure fresh
        fresh_creds = ensure_token_fresh(creds)

        # Verify
        assert fresh_creds == mock_valid_credentials
        assert is_refresh_needed(fresh_creds) is False
