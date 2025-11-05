"""Tests for authentication configuration system."""

import os
import sys
from unittest.mock import patch

import pytest

from claude_agent_sdk import AuthConfig, AuthFallbackPolicy, AuthMode
from claude_agent_sdk._internal.auth_config import (
    _detect_non_interactive,
    _str_to_bool,
    load_auth_config,
)


class TestStrToBool:
    """Test string to boolean conversion."""

    def test_true_values(self):
        """Test values that should convert to True."""
        assert _str_to_bool("true") is True
        assert _str_to_bool("True") is True
        assert _str_to_bool("TRUE") is True
        assert _str_to_bool("1") is True
        assert _str_to_bool("yes") is True
        assert _str_to_bool("y") is True
        assert _str_to_bool("on") is True

    def test_false_values(self):
        """Test values that should convert to False."""
        assert _str_to_bool("false") is False
        assert _str_to_bool("False") is False
        assert _str_to_bool("0") is False
        assert _str_to_bool("no") is False
        assert _str_to_bool("off") is False
        assert _str_to_bool("") is False
        assert _str_to_bool(None) is False


class TestDetectNonInteractive:
    """Test non-interactive environment detection."""

    def test_explicit_interactive_true(self, monkeypatch):
        """Test explicit CLAUDE_AUTH_INTERACTIVE=true."""
        monkeypatch.setenv("CLAUDE_AUTH_INTERACTIVE", "true")
        assert _detect_non_interactive() is False

    def test_explicit_interactive_false(self, monkeypatch):
        """Test explicit CLAUDE_AUTH_INTERACTIVE=false."""
        monkeypatch.setenv("CLAUDE_AUTH_INTERACTIVE", "false")
        assert _detect_non_interactive() is True

    def test_ci_environment(self, monkeypatch):
        """Test CI environment detection."""
        monkeypatch.delenv("CLAUDE_AUTH_INTERACTIVE", raising=False)
        monkeypatch.setenv("CI", "true")
        assert _detect_non_interactive() is True

    def test_github_actions(self, monkeypatch):
        """Test GitHub Actions detection."""
        monkeypatch.delenv("CLAUDE_AUTH_INTERACTIVE", raising=False)
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        assert _detect_non_interactive() is True

    def test_gitlab_ci(self, monkeypatch):
        """Test GitLab CI detection."""
        monkeypatch.delenv("CLAUDE_AUTH_INTERACTIVE", raising=False)
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        monkeypatch.setenv("GITLAB_CI", "true")
        assert _detect_non_interactive() is True

    def test_no_tty(self, monkeypatch):
        """Test no TTY detection."""
        monkeypatch.delenv("CLAUDE_AUTH_INTERACTIVE", raising=False)
        monkeypatch.delenv("CI", raising=False)
        with patch.object(sys.stdin, "isatty", return_value=False):
            assert _detect_non_interactive() is True


class TestAuthConfig:
    """Test AuthConfig dataclass."""

    def test_allow_fallback_enabled(self):
        """Test allow_fallback property with ENABLED policy."""
        config = AuthConfig(
            auth_mode=AuthMode.AUTO,
            auth_fallback=AuthFallbackPolicy.ENABLED,
            auth_interactive=True,
        )
        assert config.allow_fallback is True

    def test_allow_fallback_disabled(self):
        """Test allow_fallback property with DISABLED policy."""
        config = AuthConfig(
            auth_mode=AuthMode.AUTO,
            auth_fallback=AuthFallbackPolicy.DISABLED,
            auth_interactive=True,
        )
        assert config.allow_fallback is False

    def test_allow_fallback_strict(self):
        """Test allow_fallback property with STRICT policy."""
        config = AuthConfig(
            auth_mode=AuthMode.AUTO,
            auth_fallback=AuthFallbackPolicy.STRICT,
            auth_interactive=True,
        )
        assert config.allow_fallback is False

    def test_strict_mode_enabled(self):
        """Test strict_mode property with DISABLED policy."""
        config = AuthConfig(
            auth_mode=AuthMode.AUTO,
            auth_fallback=AuthFallbackPolicy.DISABLED,
            auth_interactive=True,
        )
        assert config.strict_mode is True

    def test_strict_mode_strict(self):
        """Test strict_mode property with STRICT policy."""
        config = AuthConfig(
            auth_mode=AuthMode.AUTO,
            auth_fallback=AuthFallbackPolicy.STRICT,
            auth_interactive=True,
        )
        assert config.strict_mode is True

    def test_strict_mode_not_enabled(self):
        """Test strict_mode property with ENABLED policy."""
        config = AuthConfig(
            auth_mode=AuthMode.AUTO,
            auth_fallback=AuthFallbackPolicy.ENABLED,
            auth_interactive=True,
        )
        assert config.strict_mode is False

    def test_format_error_message_basic(self):
        """Test basic error message formatting."""
        config = AuthConfig(
            auth_mode=AuthMode.OAUTH,
            auth_fallback=AuthFallbackPolicy.DISABLED,
            auth_interactive=False,
        )
        message = config.format_error_message("OAuth token expired")
        assert "OAuth token expired" in message
        assert "oauth" in message
        assert "disabled" in message
        assert "False" in message

    def test_format_error_message_with_suggestions(self):
        """Test error message formatting with suggestions."""
        config = AuthConfig(
            auth_mode=AuthMode.AUTO,
            auth_fallback=AuthFallbackPolicy.ENABLED,
            auth_interactive=True,
        )
        suggestions = [
            "Set ANTHROPIC_API_KEY environment variable",
            "Run: python -m claude_agent_sdk login",
        ]
        message = config.format_error_message("No authentication available", suggestions)
        assert "No authentication available" in message
        assert "Set ANTHROPIC_API_KEY" in message
        assert "python -m claude_agent_sdk login" in message
        assert "1." in message
        assert "2." in message


class TestLoadAuthConfig:
    """Test load_auth_config function."""

    def test_defaults(self, monkeypatch):
        """Test default configuration (no env vars, no SDK params)."""
        # Clear all auth-related env vars
        for key in list(os.environ.keys()):
            if key.startswith(("CLAUDE_", "ANTHROPIC_", "CI", "GITHUB_", "GITLAB_")):
                monkeypatch.delenv(key, raising=False)

        config = load_auth_config()
        assert config.auth_mode == AuthMode.AUTO
        assert config.auth_fallback == AuthFallbackPolicy.ENABLED
        # auth_interactive depends on TTY, so we don't assert exact value
        assert config.api_key is None

    def test_api_key_from_env(self, monkeypatch):
        """Test API key loaded from environment."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test123")
        config = load_auth_config()
        assert config.api_key == "sk-ant-test123"

    def test_auth_mode_from_env(self, monkeypatch):
        """Test auth_mode from environment variable."""
        monkeypatch.setenv("CLAUDE_AUTH_MODE", "oauth")
        config = load_auth_config()
        assert config.auth_mode == AuthMode.OAUTH

    def test_auth_mode_case_insensitive(self, monkeypatch):
        """Test auth_mode is case-insensitive."""
        monkeypatch.setenv("CLAUDE_AUTH_MODE", "OAUTH")
        config = load_auth_config()
        assert config.auth_mode == AuthMode.OAUTH

    def test_auth_mode_invalid_defaults_to_auto(self, monkeypatch):
        """Test invalid auth_mode defaults to AUTO."""
        monkeypatch.setenv("CLAUDE_AUTH_MODE", "invalid")
        config = load_auth_config()
        assert config.auth_mode == AuthMode.AUTO

    def test_auth_fallback_true_from_env(self, monkeypatch):
        """Test auth_fallback=true from environment."""
        monkeypatch.setenv("CLAUDE_AUTH_FALLBACK", "true")
        config = load_auth_config()
        assert config.auth_fallback == AuthFallbackPolicy.ENABLED

    def test_auth_fallback_false_from_env(self, monkeypatch):
        """Test auth_fallback=false from environment."""
        monkeypatch.setenv("CLAUDE_AUTH_FALLBACK", "false")
        config = load_auth_config()
        assert config.auth_fallback == AuthFallbackPolicy.DISABLED

    def test_auth_strict_overrides_fallback(self, monkeypatch):
        """Test CLAUDE_AUTH_STRICT overrides CLAUDE_AUTH_FALLBACK."""
        monkeypatch.setenv("CLAUDE_AUTH_FALLBACK", "true")
        monkeypatch.setenv("CLAUDE_AUTH_STRICT", "true")
        config = load_auth_config()
        assert config.auth_fallback == AuthFallbackPolicy.STRICT

    def test_legacy_use_subscription(self, monkeypatch):
        """Test CLAUDE_USE_SUBSCRIPTION=true maps to OAuth mode."""
        monkeypatch.setenv("CLAUDE_USE_SUBSCRIPTION", "true")
        config = load_auth_config()
        assert config.auth_mode == AuthMode.OAUTH

    def test_auth_mode_env_overrides_legacy(self, monkeypatch):
        """Test CLAUDE_AUTH_MODE overrides CLAUDE_USE_SUBSCRIPTION."""
        monkeypatch.setenv("CLAUDE_USE_SUBSCRIPTION", "true")
        monkeypatch.setenv("CLAUDE_AUTH_MODE", "api_key")
        config = load_auth_config()
        assert config.auth_mode == AuthMode.API_KEY

    def test_sdk_auth_mode_string(self, monkeypatch):
        """Test SDK auth_mode as string."""
        # Clear env vars
        for key in list(os.environ.keys()):
            if key.startswith("CLAUDE_AUTH"):
                monkeypatch.delenv(key, raising=False)

        config = load_auth_config(sdk_auth_mode="oauth")
        assert config.auth_mode == AuthMode.OAUTH

    def test_sdk_auth_mode_enum(self, monkeypatch):
        """Test SDK auth_mode as enum."""
        for key in list(os.environ.keys()):
            if key.startswith("CLAUDE_AUTH"):
                monkeypatch.delenv(key, raising=False)

        config = load_auth_config(sdk_auth_mode=AuthMode.API_KEY)
        assert config.auth_mode == AuthMode.API_KEY

    def test_sdk_auth_fallback_string(self, monkeypatch):
        """Test SDK auth_fallback as string."""
        for key in list(os.environ.keys()):
            if key.startswith("CLAUDE_AUTH"):
                monkeypatch.delenv(key, raising=False)

        config = load_auth_config(sdk_auth_fallback="disabled")
        assert config.auth_fallback == AuthFallbackPolicy.DISABLED

    def test_sdk_auth_fallback_enum(self, monkeypatch):
        """Test SDK auth_fallback as enum."""
        for key in list(os.environ.keys()):
            if key.startswith("CLAUDE_AUTH"):
                monkeypatch.delenv(key, raising=False)

        config = load_auth_config(sdk_auth_fallback=AuthFallbackPolicy.STRICT)
        assert config.auth_fallback == AuthFallbackPolicy.STRICT

    def test_sdk_auth_interactive(self, monkeypatch):
        """Test SDK auth_interactive parameter."""
        for key in list(os.environ.keys()):
            if key.startswith("CLAUDE_AUTH"):
                monkeypatch.delenv(key, raising=False)
        monkeypatch.delenv("CI", raising=False)

        config = load_auth_config(sdk_auth_interactive=False)
        assert config.auth_interactive is False

    def test_env_overrides_sdk(self, monkeypatch):
        """Test environment variables override SDK parameters."""
        monkeypatch.setenv("CLAUDE_AUTH_MODE", "oauth")
        monkeypatch.setenv("CLAUDE_AUTH_FALLBACK", "false")
        monkeypatch.setenv("CLAUDE_AUTH_INTERACTIVE", "false")

        config = load_auth_config(
            sdk_auth_mode=AuthMode.API_KEY,
            sdk_auth_fallback=AuthFallbackPolicy.ENABLED,
            sdk_auth_interactive=True,
        )

        # Environment wins
        assert config.auth_mode == AuthMode.OAUTH
        assert config.auth_fallback == AuthFallbackPolicy.DISABLED
        assert config.auth_interactive is False

    def test_full_configuration_chain(self, monkeypatch):
        """Test complete configuration with all precedence levels."""
        # Set environment (highest priority)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-env-key")
        monkeypatch.setenv("CLAUDE_AUTH_MODE", "oauth")
        monkeypatch.setenv("CLAUDE_AUTH_STRICT", "true")
        monkeypatch.setenv("CLAUDE_AUTH_INTERACTIVE", "false")

        # SDK config (lower priority)
        config = load_auth_config(
            sdk_auth_mode=AuthMode.API_KEY,  # Should be overridden
            sdk_auth_fallback=AuthFallbackPolicy.ENABLED,  # Should be overridden
            sdk_auth_interactive=True,  # Should be overridden
        )

        # Verify environment wins
        assert config.api_key == "sk-ant-env-key"
        assert config.auth_mode == AuthMode.OAUTH
        assert config.auth_fallback == AuthFallbackPolicy.STRICT
        assert config.auth_interactive is False


class TestAuthConfigIntegration:
    """Integration tests for auth configuration scenarios."""

    def test_oauth_first_with_fallback(self, monkeypatch):
        """Test default OAuth-first with fallback configuration."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        config = load_auth_config()

        assert config.auth_mode == AuthMode.AUTO
        assert config.allow_fallback is True
        assert config.api_key == "sk-ant-test"

    def test_api_key_only_no_oauth(self, monkeypatch):
        """Test API key only mode (skip OAuth)."""
        monkeypatch.setenv("CLAUDE_AUTH_MODE", "api_key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        config = load_auth_config()

        assert config.auth_mode == AuthMode.API_KEY
        assert config.api_key == "sk-ant-test"

    def test_oauth_strict_no_fallback(self, monkeypatch):
        """Test OAuth strict mode (no fallback)."""
        monkeypatch.setenv("CLAUDE_AUTH_MODE", "oauth")
        monkeypatch.setenv("CLAUDE_AUTH_FALLBACK", "false")
        config = load_auth_config()

        assert config.auth_mode == AuthMode.OAUTH
        assert config.allow_fallback is False
        assert config.strict_mode is True

    def test_non_interactive_server_mode(self, monkeypatch):
        """Test non-interactive server/CI mode."""
        monkeypatch.setenv("CLAUDE_AUTH_INTERACTIVE", "false")
        monkeypatch.setenv("CI", "true")
        config = load_auth_config()

        assert config.auth_interactive is False

    def test_ci_auto_detect_non_interactive(self, monkeypatch):
        """Test CI environment auto-detects non-interactive."""
        monkeypatch.delenv("CLAUDE_AUTH_INTERACTIVE", raising=False)
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        config = load_auth_config()

        assert config.auth_interactive is False
