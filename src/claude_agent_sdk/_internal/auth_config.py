"""Authentication configuration system for Claude SDK.

This module provides a hierarchical configuration system for authentication:
- Environment variables (highest priority)
- SDK ClaudeAgentOptions config
- Default values (lowest priority)

Supports multiple authentication modes (OAuth, API key, auto-detection) and
fallback policies (enabled, disabled, strict).
"""

import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Literal


class AuthMode(Enum):
    """Authentication mode configuration.

    Attributes:
        AUTO: Smart detection - try OAuth first, fall back to API key if configured
        OAUTH: Use OAuth tokens exclusively
        API_KEY: Use API key exclusively (skip OAuth)
    """
    AUTO = "auto"
    OAUTH = "oauth"
    API_KEY = "api_key"


class AuthFallbackPolicy(Enum):
    """Authentication fallback policy configuration.

    Attributes:
        ENABLED: Allow fallback from OAuth to API key on failure (default)
        DISABLED: No fallback - error if primary auth method fails
        STRICT: Same as DISABLED (alias for clarity)
    """
    ENABLED = "enabled"
    DISABLED = "disabled"
    STRICT = "strict"


def _str_to_bool(value: str | None) -> bool:
    """Convert string to boolean.

    Args:
        value: String value to convert (case-insensitive)

    Returns:
        True if value is "true", "1", "yes", "y", "on"
        False otherwise
    """
    if value is None:
        return False
    return value.lower() in ("true", "1", "yes", "y", "on")


def _detect_non_interactive() -> bool:
    """Detect if running in non-interactive environment.

    Checks for:
    - CI/CD environment variables (CI, GITHUB_ACTIONS, etc.)
    - No TTY attached to stdin
    - Explicit CLAUDE_AUTH_INTERACTIVE=false

    Returns:
        True if non-interactive environment detected
    """
    # Explicit override
    interactive_env = os.getenv("CLAUDE_AUTH_INTERACTIVE")
    if interactive_env is not None:
        return not _str_to_bool(interactive_env)

    # Check for CI/CD environments
    ci_vars = [
        "CI",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "CIRCLECI",
        "TRAVIS",
        "JENKINS_HOME",
        "TEAMCITY_VERSION",
        "BUILDKITE",
    ]
    if any(os.getenv(var) for var in ci_vars):
        return True

    # Check if stdin has a TTY
    if not sys.stdin.isatty():
        return True

    return False


@dataclass
class AuthConfig:
    """Authentication configuration with precedence handling.

    Configuration precedence (highest to lowest):
    1. Environment variables
    2. SDK ClaudeAgentOptions parameters
    3. Default values

    Attributes:
        auth_mode: Primary authentication method (AUTO, OAUTH, or API_KEY)
        auth_fallback: Fallback policy (ENABLED, DISABLED, or STRICT)
        auth_interactive: Whether browser login prompts are allowed
        api_key: Explicit API key (from ANTHROPIC_API_KEY)
    """
    auth_mode: AuthMode
    auth_fallback: AuthFallbackPolicy
    auth_interactive: bool
    api_key: str | None = None

    @property
    def allow_fallback(self) -> bool:
        """Check if fallback to API key is allowed.

        Returns:
            True if fallback is enabled, False for disabled/strict modes
        """
        return self.auth_fallback == AuthFallbackPolicy.ENABLED

    @property
    def strict_mode(self) -> bool:
        """Check if strict mode is enabled (no fallback).

        Returns:
            True if fallback is disabled or strict
        """
        return self.auth_fallback in (AuthFallbackPolicy.DISABLED, AuthFallbackPolicy.STRICT)

    def format_error_message(
        self,
        error: str,
        suggestions: list[str] | None = None
    ) -> str:
        """Format authentication error message with suggestions.

        Args:
            error: Main error message
            suggestions: List of suggested resolution steps

        Returns:
            Formatted error message with context and suggestions
        """
        lines = [
            "Authentication Error",
            "-" * 50,
            f"Error: {error}",
            "",
            "Configuration:",
            f"  Mode: {self.auth_mode.value}",
            f"  Fallback: {self.auth_fallback.value}",
            f"  Interactive: {self.auth_interactive}",
        ]

        if suggestions:
            lines.extend(["", "Suggestions:"])
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        return "\n".join(lines)


def load_auth_config(
    sdk_auth_mode: str | AuthMode | None = None,
    sdk_auth_fallback: str | AuthFallbackPolicy | None = None,
    sdk_auth_interactive: bool | None = None,
) -> AuthConfig:
    """Load authentication configuration with precedence handling.

    Configuration precedence (highest to lowest):
    1. Environment variables
    2. SDK parameters
    3. Default values

    Environment Variables:
        ANTHROPIC_API_KEY: API key for authentication
        CLAUDE_AUTH_MODE: Authentication mode (auto|oauth|api_key)
        CLAUDE_AUTH_FALLBACK: Fallback policy (true|false)
        CLAUDE_AUTH_STRICT: Strict mode flag (true|false)
        CLAUDE_AUTH_INTERACTIVE: Allow browser login (true|false)
        CLAUDE_USE_SUBSCRIPTION: Legacy - maps to CLAUDE_AUTH_MODE=oauth

    Args:
        sdk_auth_mode: SDK-provided auth mode (overridden by env vars)
        sdk_auth_fallback: SDK-provided fallback policy (overridden by env vars)
        sdk_auth_interactive: SDK-provided interactive flag (overridden by env vars)

    Returns:
        AuthConfig with resolved configuration
    """
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")

    # Resolve auth_mode (env > sdk > default)
    mode_str = os.getenv("CLAUDE_AUTH_MODE")

    # Legacy compatibility: CLAUDE_USE_SUBSCRIPTION=true -> oauth mode
    if mode_str is None and _str_to_bool(os.getenv("CLAUDE_USE_SUBSCRIPTION")):
        mode_str = "oauth"

    if mode_str:
        # Environment variable wins
        try:
            auth_mode = AuthMode(mode_str.lower())
        except ValueError:
            # Invalid mode, default to AUTO
            auth_mode = AuthMode.AUTO
    elif sdk_auth_mode:
        # SDK parameter
        if isinstance(sdk_auth_mode, AuthMode):
            auth_mode = sdk_auth_mode
        else:
            try:
                auth_mode = AuthMode(sdk_auth_mode.lower())
            except ValueError:
                auth_mode = AuthMode.AUTO
    else:
        # Default
        auth_mode = AuthMode.AUTO

    # Resolve auth_fallback (env > sdk > default)
    # CLAUDE_AUTH_STRICT overrides CLAUDE_AUTH_FALLBACK
    strict_env = os.getenv("CLAUDE_AUTH_STRICT")
    if strict_env is not None and _str_to_bool(strict_env):
        auth_fallback = AuthFallbackPolicy.STRICT
    else:
        fallback_env = os.getenv("CLAUDE_AUTH_FALLBACK")
        if fallback_env:
            # Environment variable
            if _str_to_bool(fallback_env):
                auth_fallback = AuthFallbackPolicy.ENABLED
            else:
                auth_fallback = AuthFallbackPolicy.DISABLED
        elif sdk_auth_fallback:
            # SDK parameter
            if isinstance(sdk_auth_fallback, AuthFallbackPolicy):
                auth_fallback = sdk_auth_fallback
            else:
                try:
                    auth_fallback = AuthFallbackPolicy(sdk_auth_fallback.lower())
                except ValueError:
                    auth_fallback = AuthFallbackPolicy.ENABLED
        else:
            # Default: enabled
            auth_fallback = AuthFallbackPolicy.ENABLED

    # Resolve auth_interactive (env > sdk > auto-detect)
    interactive_env = os.getenv("CLAUDE_AUTH_INTERACTIVE")
    if interactive_env is not None:
        # Environment variable wins
        auth_interactive = _str_to_bool(interactive_env)
    elif sdk_auth_interactive is not None:
        # SDK parameter
        auth_interactive = sdk_auth_interactive
    else:
        # Auto-detect (default: True unless CI/no TTY)
        auth_interactive = not _detect_non_interactive()

    return AuthConfig(
        auth_mode=auth_mode,
        auth_fallback=auth_fallback,
        auth_interactive=auth_interactive,
        api_key=api_key,
    )
