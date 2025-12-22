"""Tests for authentication integration in SubprocessCLITransport."""

import os
from unittest.mock import MagicMock, patch

import pytest

from claude_agent_sdk._errors import CLIConnectionError
from claude_agent_sdk._internal.auth_manager import AuthenticationResult, AuthState
from claude_agent_sdk._internal.oauth_credentials import OAuthCredentials
from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport
from claude_agent_sdk.types import ClaudeAgentOptions


class TestTransportAuthIntegration:
    """Test authentication integration in subprocess transport."""

    def test_build_auth_env_with_oauth_mode(self):
        """Test environment variables for OAuth mode."""
        with patch(
            "claude_agent_sdk._internal.auth_manager.AuthenticationManager"
        ) as mock_auth_manager_class:
            # Setup mock to return OAuth result
            mock_auth_manager = MagicMock()
            mock_auth_manager_class.return_value = mock_auth_manager
            mock_auth_manager.ensure_authenticated.return_value = AuthenticationResult(
                state=AuthState.OAUTH_VALID,
                credentials=OAuthCredentials(
                    access_token="sk-ant-oat01-test",
                    refresh_token="sk-ant-ort01-test",
                    expires_at=9999999999999,
                    scopes=["user:inference"],
                    subscription="max",
                ),
            )

            # Create transport with OAuth config
            options = ClaudeAgentOptions(auth_mode="oauth")
            transport = SubprocessCLITransport(prompt="test", options=options)

            # Build auth environment
            auth_env = transport._build_auth_env()

            # Verify OAuth environment variables
            assert auth_env.get("CLAUDE_USE_SUBSCRIPTION") == "true"
            assert "ANTHROPIC_API_KEY" not in auth_env

    def test_build_auth_env_with_api_key_mode(self):
        """Test environment variables for API key mode."""
        with patch(
            "claude_agent_sdk._internal.auth_manager.AuthenticationManager"
        ) as mock_auth_manager_class:
            # Setup mock to return API key result
            mock_auth_manager = MagicMock()
            mock_auth_manager_class.return_value = mock_auth_manager
            mock_auth_manager.ensure_authenticated.return_value = AuthenticationResult(
                state=AuthState.API_KEY_MODE, api_key="sk-ant-api01-test-key"
            )

            # Create transport with API key
            os.environ["ANTHROPIC_API_KEY"] = "sk-ant-api01-test-key"
            try:
                options = ClaudeAgentOptions(auth_mode="api_key")
                transport = SubprocessCLITransport(prompt="test", options=options)

                # Build auth environment
                auth_env = transport._build_auth_env()

                # Verify API key environment variable
                assert auth_env.get("ANTHROPIC_API_KEY") == "sk-ant-api01-test-key"
                assert "CLAUDE_USE_SUBSCRIPTION" not in auth_env
            finally:
                del os.environ["ANTHROPIC_API_KEY"]

    def test_build_auth_env_with_auth_failed(self):
        """Test error handling when authentication fails."""
        with patch(
            "claude_agent_sdk._internal.auth_manager.AuthenticationManager"
        ) as mock_auth_manager_class:
            # Setup mock to return failed auth
            mock_auth_manager = MagicMock()
            mock_auth_manager_class.return_value = mock_auth_manager
            mock_auth_manager.ensure_authenticated.return_value = AuthenticationResult(
                state=AuthState.AUTH_FAILED,
                error="No valid authentication method available",
            )

            # Create transport
            options = ClaudeAgentOptions()
            transport = SubprocessCLITransport(prompt="test", options=options)

            # Should raise CLIConnectionError
            with pytest.raises(CLIConnectionError, match="No valid authentication"):
                transport._build_auth_env()

    def test_build_auth_env_with_strict_mode_error(self):
        """Test error handling when strict mode raises RuntimeError."""
        with patch(
            "claude_agent_sdk._internal.auth_manager.AuthenticationManager"
        ) as mock_auth_manager_class:
            # Setup mock to raise RuntimeError (strict mode)
            mock_auth_manager = MagicMock()
            mock_auth_manager_class.return_value = mock_auth_manager
            mock_auth_manager.ensure_authenticated.side_effect = RuntimeError(
                "Authentication failed in strict mode"
            )

            # Create transport with strict mode
            options = ClaudeAgentOptions()
            transport = SubprocessCLITransport(prompt="test", options=options)

            # Should raise CLIConnectionError
            with pytest.raises(
                CLIConnectionError, match="Authentication failed in strict mode"
            ):
                transport._build_auth_env()

    def test_build_auth_env_passes_options_to_manager(self):
        """Test that auth options are correctly passed to AuthenticationManager."""
        with patch(
            "claude_agent_sdk._internal.auth_manager.AuthenticationManager"
        ) as mock_auth_manager_class:
            # Setup mock
            mock_auth_manager = MagicMock()
            mock_auth_manager_class.return_value = mock_auth_manager
            mock_auth_manager.ensure_authenticated.return_value = AuthenticationResult(
                state=AuthState.API_KEY_MODE, api_key="test-key"
            )

            # Create transport with specific auth options
            options = ClaudeAgentOptions(
                auth_mode="oauth",
                auth_fallback="enabled",
                auth_interactive=True,
            )
            transport = SubprocessCLITransport(prompt="test", options=options)

            # Build auth environment
            transport._build_auth_env()

            # Verify manager was created with correct options
            mock_auth_manager_class.assert_called_once_with(
                auth_mode="oauth", auth_fallback="enabled", auth_interactive=True
            )

    def test_build_auth_env_with_enum_fallback_policy(self):
        """Test that AuthFallbackPolicy enum is converted to string."""
        from claude_agent_sdk._internal.auth_config import AuthFallbackPolicy

        with patch(
            "claude_agent_sdk._internal.auth_manager.AuthenticationManager"
        ) as mock_auth_manager_class:
            # Setup mock
            mock_auth_manager = MagicMock()
            mock_auth_manager_class.return_value = mock_auth_manager
            mock_auth_manager.ensure_authenticated.return_value = AuthenticationResult(
                state=AuthState.API_KEY_MODE, api_key="test-key"
            )

            # Create transport with enum fallback policy
            options = ClaudeAgentOptions(
                auth_mode="oauth", auth_fallback=AuthFallbackPolicy.STRICT
            )
            transport = SubprocessCLITransport(prompt="test", options=options)

            # Build auth environment
            transport._build_auth_env()

            # Verify manager was called with string version of enum
            call_args = mock_auth_manager_class.call_args
            assert call_args[1]["auth_fallback"] == "strict"
