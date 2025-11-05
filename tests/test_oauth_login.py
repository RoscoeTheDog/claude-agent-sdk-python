"""Tests for OAuth login delegation module."""

import subprocess
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from claude_agent_sdk._internal.oauth_credentials import OAuthCredentials
from claude_agent_sdk._internal.oauth_login import (
    check_claude_cli_installed,
    ensure_valid_credentials,
    get_claude_cli_version,
    trigger_oauth_login,
)


@pytest.fixture
def mock_valid_credentials():
    """Mock valid OAuth credentials."""
    return OAuthCredentials(
        access_token="sk-ant-oat01-test-access-token",
        refresh_token="sk-ant-ort01-test-refresh-token",
        expires_at=int(
            (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp() * 1000
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


class TestTriggerOAuthLogin:
    """Tests for trigger_oauth_login function."""

    def test_non_interactive_raises_error(self):
        """Test that non-interactive mode raises error."""
        with pytest.raises(RuntimeError, match="non-interactive mode"):
            trigger_oauth_login(interactive=False)

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    @patch("claude_agent_sdk._internal.oauth_login.read_credentials")
    def test_successful_login(self, mock_read, mock_subprocess, mock_valid_credentials):
        """Test successful OAuth login flow."""
        # Mock successful subprocess call
        mock_subprocess.return_value = Mock(returncode=0)

        # Mock credentials created after login
        mock_read.return_value = mock_valid_credentials

        result = trigger_oauth_login(interactive=True)

        assert result is True
        mock_subprocess.assert_called_once_with(
            ["claude", "/login"],
            check=True,
            text=True,
        )
        mock_read.assert_called_once()

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    @patch("claude_agent_sdk._internal.oauth_login.read_credentials")
    def test_login_failed_no_credentials(self, mock_read, mock_subprocess):
        """Test login failure when no credentials created."""
        # Mock successful subprocess but no credentials created
        mock_subprocess.return_value = Mock(returncode=0)
        mock_read.return_value = None

        result = trigger_oauth_login(interactive=True)

        assert result is False

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    @patch("claude_agent_sdk._internal.oauth_login.read_credentials")
    def test_login_failed_expired_credentials(
        self, mock_read, mock_subprocess, mock_expired_credentials
    ):
        """Test login failure when credentials still expired."""
        # Mock successful subprocess but expired credentials
        mock_subprocess.return_value = Mock(returncode=0)
        mock_read.return_value = mock_expired_credentials

        result = trigger_oauth_login(interactive=True)

        assert result is False

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_claude_cli_not_found(self, mock_subprocess):
        """Test handling of missing Claude CLI."""
        mock_subprocess.side_effect = FileNotFoundError("claude not found")

        result = trigger_oauth_login(interactive=True)

        assert result is False

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_subprocess_error(self, mock_subprocess):
        """Test handling of subprocess errors."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            1, "claude /login", stderr="Login failed"
        )

        result = trigger_oauth_login(interactive=True)

        assert result is False

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_keyboard_interrupt(self, mock_subprocess):
        """Test handling of user cancellation."""
        mock_subprocess.side_effect = KeyboardInterrupt()

        result = trigger_oauth_login(interactive=True)

        assert result is False


class TestEnsureValidCredentials:
    """Tests for ensure_valid_credentials function."""

    @patch("claude_agent_sdk._internal.oauth_login.read_credentials")
    def test_valid_credentials_exist(self, mock_read, mock_valid_credentials):
        """Test when valid credentials already exist."""
        mock_read.return_value = mock_valid_credentials

        creds = ensure_valid_credentials(interactive=True)

        assert creds == mock_valid_credentials
        # Should not trigger login
        mock_read.assert_called_once()

    @patch("claude_agent_sdk._internal.oauth_login.read_credentials")
    def test_no_credentials_non_interactive(self, mock_read):
        """Test error when no credentials in non-interactive mode."""
        mock_read.return_value = None

        with pytest.raises(RuntimeError, match="non-interactive mode"):
            ensure_valid_credentials(interactive=False)

    @patch("claude_agent_sdk._internal.oauth_login.trigger_oauth_login")
    @patch("claude_agent_sdk._internal.oauth_login.read_credentials")
    def test_expired_credentials_successful_refresh(
        self, mock_read, mock_trigger, mock_expired_credentials, mock_valid_credentials
    ):
        """Test successful refresh of expired credentials."""
        # First call: expired credentials
        # Second call (after login): valid credentials
        mock_read.side_effect = [mock_expired_credentials, mock_valid_credentials]
        mock_trigger.return_value = True

        creds = ensure_valid_credentials(interactive=True)

        assert creds == mock_valid_credentials
        mock_trigger.assert_called_once_with(interactive=True)

    @patch("claude_agent_sdk._internal.oauth_login.trigger_oauth_login")
    @patch("claude_agent_sdk._internal.oauth_login.read_credentials")
    def test_login_failed(self, mock_read, mock_trigger, mock_expired_credentials):
        """Test error when login fails."""
        mock_read.return_value = mock_expired_credentials
        mock_trigger.return_value = False

        with pytest.raises(
            RuntimeError, match="Failed to obtain valid OAuth credentials"
        ):
            ensure_valid_credentials(interactive=True)

    @patch("claude_agent_sdk._internal.oauth_login.trigger_oauth_login")
    @patch("claude_agent_sdk._internal.oauth_login.read_credentials")
    def test_login_succeeded_but_credentials_still_invalid(
        self, mock_read, mock_trigger, mock_expired_credentials
    ):
        """Test error when login succeeds but credentials still invalid."""
        # First call: expired
        # Second call (after login): still expired
        mock_read.side_effect = [mock_expired_credentials, mock_expired_credentials]
        mock_trigger.return_value = True

        with pytest.raises(RuntimeError, match="Login appeared to succeed"):
            ensure_valid_credentials(interactive=True)


class TestCheckClaudeCLIInstalled:
    """Tests for check_claude_cli_installed function."""

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_claude_installed(self, mock_subprocess):
        """Test when Claude CLI is installed."""
        mock_subprocess.return_value = Mock(returncode=0)

        result = check_claude_cli_installed()

        assert result is True
        mock_subprocess.assert_called_once()

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_claude_not_installed(self, mock_subprocess):
        """Test when Claude CLI is not installed."""
        mock_subprocess.side_effect = FileNotFoundError()

        result = check_claude_cli_installed()

        assert result is False

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_claude_command_fails(self, mock_subprocess):
        """Test when Claude CLI command fails."""
        mock_subprocess.return_value = Mock(returncode=1)

        result = check_claude_cli_installed()

        assert result is False

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_claude_timeout(self, mock_subprocess):
        """Test when Claude CLI times out."""
        mock_subprocess.side_effect = subprocess.TimeoutExpired("claude --version", 5)

        result = check_claude_cli_installed()

        assert result is False


class TestGetClaudeCLIVersion:
    """Tests for get_claude_cli_version function."""

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_get_version_success(self, mock_subprocess):
        """Test successful version retrieval."""
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="claude-code version 1.0.123\n",
        )

        version = get_claude_cli_version()

        assert version == "1.0.123"

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_get_version_different_format(self, mock_subprocess):
        """Test version retrieval with different output format."""
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="Claude Code CLI v2.0.0",
        )

        version = get_claude_cli_version()

        # Should return last token
        assert "2.0.0" in version or version == "Claude Code CLI v2.0.0"

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_get_version_not_installed(self, mock_subprocess):
        """Test version retrieval when CLI not installed."""
        mock_subprocess.side_effect = FileNotFoundError()

        version = get_claude_cli_version()

        assert version is None

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_get_version_timeout(self, mock_subprocess):
        """Test version retrieval timeout."""
        mock_subprocess.side_effect = subprocess.TimeoutExpired("claude --version", 5)

        version = get_claude_cli_version()

        assert version is None

    @patch("claude_agent_sdk._internal.oauth_login.subprocess.run")
    def test_get_version_error(self, mock_subprocess):
        """Test version retrieval error."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            1, "claude --version"
        )

        version = get_claude_cli_version()

        assert version is None
