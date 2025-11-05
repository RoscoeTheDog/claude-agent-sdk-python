"""Smart Authentication Manager for Claude SDK.

This module implements an intelligent authentication system that:
- Auto-detects authentication mode (OAuth vs API key)
- Checks token validity before each request
- Auto-refreshes expired access tokens
- Auto-triggers browser login if refresh token expired (interactive mode)
- Respects fallback policy (error vs fallback to API key)

The manager uses a state machine to track authentication state and
handle transitions gracefully with minimal user disruption.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from enum import Enum

from .auth_config import AuthMode, load_auth_config
from .oauth_credentials import (
    OAuthCredentials,
    read_credentials,
)
from .oauth_login import trigger_oauth_login
from .oauth_refresh import refresh_oauth_token


class AuthState(Enum):
    """Authentication state machine states.

    States:
        API_KEY_MODE: Using ANTHROPIC_API_KEY (explicit or fallback)
        OAUTH_VALID: OAuth tokens valid, ready to use
        OAUTH_REFRESH_NEEDED: Access token expired, refresh token valid
        OAUTH_LOGIN_NEEDED: No credentials or refresh token expired
        AUTH_FAILED: All auth methods exhausted based on config
    """

    API_KEY_MODE = "api_key_mode"
    OAUTH_VALID = "oauth_valid"
    OAUTH_REFRESH_NEEDED = "oauth_refresh_needed"
    OAUTH_LOGIN_NEEDED = "oauth_login_needed"
    AUTH_FAILED = "auth_failed"


@dataclass
class AuthenticationResult:
    """Result of authentication check/refresh operation.

    Attributes:
        state: Current authentication state
        credentials: OAuth credentials (if OAuth mode)
        api_key: API key (if API key mode)
        error: Error message (if AUTH_FAILED state)
    """

    state: AuthState
    credentials: OAuthCredentials | None = None
    api_key: str | None = None
    error: str | None = None

    @property
    def is_oauth(self) -> bool:
        """Check if using OAuth authentication."""
        return self.state in (AuthState.OAUTH_VALID, AuthState.OAUTH_REFRESH_NEEDED)

    @property
    def is_api_key(self) -> bool:
        """Check if using API key authentication."""
        return self.state == AuthState.API_KEY_MODE

    @property
    def is_ready(self) -> bool:
        """Check if authentication is ready for use."""
        return self.state in (AuthState.API_KEY_MODE, AuthState.OAUTH_VALID)

    def get_auth_header(self) -> dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            Dictionary with appropriate auth headers:
            - OAuth: {"Authorization": "Bearer <token>"}
            - API Key: {"x-api-key": "<key>"}

        Raises:
            RuntimeError: If authentication is not ready
        """
        if not self.is_ready:
            raise RuntimeError(
                f"Authentication not ready. Current state: {self.state.value}"
            )

        if self.is_oauth:
            if not self.credentials:
                raise RuntimeError("OAuth credentials missing")
            return {"Authorization": f"Bearer {self.credentials.access_token}"}
        elif self.is_api_key:
            if not self.api_key:
                raise RuntimeError("API key missing")
            return {"x-api-key": self.api_key}
        else:
            raise RuntimeError(f"Unexpected auth state: {self.state.value}")


class AuthenticationManager:
    """Intelligent authentication manager with state machine.

    This manager handles the full authentication lifecycle:
    1. Auto-detect authentication mode from config
    2. Check token validity before requests
    3. Auto-refresh expired tokens
    4. Auto-trigger browser login when needed
    5. Handle fallback to API key per config

    Example:
        >>> # Create manager with default config
        >>> manager = AuthenticationManager()
        >>> result = manager.ensure_authenticated()
        >>> if result.is_ready:
        ...     headers = result.get_auth_header()
        ...     # Use headers for API request

        >>> # Create manager with custom config
        >>> manager = AuthenticationManager(
        ...     auth_mode="oauth",
        ...     auth_fallback="disabled"
        ... )
    """

    def __init__(
        self,
        auth_mode: str | AuthMode | None = None,
        auth_fallback: str | None = None,
        auth_interactive: bool | None = None,
    ):
        """Initialize authentication manager.

        Args:
            auth_mode: Authentication mode (auto|oauth|api_key)
            auth_fallback: Fallback policy (enabled|disabled|strict)
            auth_interactive: Allow browser login prompts
        """
        self.config = load_auth_config(
            sdk_auth_mode=auth_mode,
            sdk_auth_fallback=auth_fallback,
            sdk_auth_interactive=auth_interactive,
        )
        self._current_state: AuthState | None = None
        self._current_credentials: OAuthCredentials | None = None

    def detect_auth_state(self) -> AuthState:
        """Detect current authentication state.

        Returns:
            Current AuthState based on config and available credentials
        """
        # If explicitly API key mode, use that
        if self.config.auth_mode == AuthMode.API_KEY:
            if self.config.api_key:
                return AuthState.API_KEY_MODE
            else:
                return AuthState.AUTH_FAILED

        # Try OAuth first (for AUTO and OAUTH modes)
        try:
            creds = read_credentials()
            if creds:
                if creds.is_valid:
                    self._current_credentials = creds
                    return AuthState.OAUTH_VALID
                elif creds.is_expired:
                    self._current_credentials = creds
                    return AuthState.OAUTH_REFRESH_NEEDED
        except Exception:
            # Credentials read failed
            pass

        # No valid OAuth credentials - determine fallback behavior
        # Check if we should fallback to API key
        if self.config.auth_mode == AuthMode.AUTO and self.config.allow_fallback:
            if self.config.api_key:
                warnings.warn(
                    "OAuth credentials not available, falling back to API key mode. "
                    "Set CLAUDE_AUTH_MODE=oauth to require OAuth authentication.",
                    stacklevel=2,
                )
                return AuthState.API_KEY_MODE

        # OAuth mode required but not available
        # Return OAUTH_LOGIN_NEEDED to trigger login flow
        return AuthState.OAUTH_LOGIN_NEEDED

    def handle_oauth_refresh(self) -> AuthenticationResult:
        """Handle OAuth token refresh.

        Returns:
            AuthenticationResult with updated state
        """
        # Attempt to refresh token
        refreshed_creds = refresh_oauth_token(interactive=self.config.auth_interactive)

        if refreshed_creds and refreshed_creds.is_valid:
            # Refresh succeeded
            self._current_credentials = refreshed_creds
            self._current_state = AuthState.OAUTH_VALID
            return AuthenticationResult(
                state=AuthState.OAUTH_VALID, credentials=refreshed_creds
            )

        # Refresh failed
        if self.config.allow_fallback and self.config.api_key:
            # Fallback to API key
            warnings.warn(
                "OAuth token refresh failed, falling back to API key mode.",
                stacklevel=2,
            )
            self._current_state = AuthState.API_KEY_MODE
            return AuthenticationResult(
                state=AuthState.API_KEY_MODE, api_key=self.config.api_key
            )
        else:
            # No fallback allowed or no API key
            self._current_state = AuthState.AUTH_FAILED
            error = self.config.format_error_message(
                "OAuth token refresh failed",
                suggestions=[
                    "Run 'claude /login' to re-authenticate",
                    "Set ANTHROPIC_API_KEY environment variable",
                    "Set CLAUDE_AUTH_FALLBACK=true to allow fallback to API key",
                ],
            )
            return AuthenticationResult(state=AuthState.AUTH_FAILED, error=error)

    def handle_oauth_login(self) -> AuthenticationResult:
        """Handle OAuth login flow.

        Returns:
            AuthenticationResult with updated state
        """
        if not self.config.auth_interactive:
            # Non-interactive mode, cannot login
            if self.config.allow_fallback and self.config.api_key:
                warnings.warn(
                    "OAuth login required but running in non-interactive mode. "
                    "Falling back to API key mode.",
                    stacklevel=2,
                )
                self._current_state = AuthState.API_KEY_MODE
                return AuthenticationResult(
                    state=AuthState.API_KEY_MODE, api_key=self.config.api_key
                )
            else:
                self._current_state = AuthState.AUTH_FAILED
                error = self.config.format_error_message(
                    "OAuth login required but running in non-interactive mode",
                    suggestions=[
                        "Run 'claude /login' manually before running your script",
                        "Set ANTHROPIC_API_KEY environment variable",
                        "Set CLAUDE_AUTH_INTERACTIVE=true to allow browser login",
                    ],
                )
                return AuthenticationResult(state=AuthState.AUTH_FAILED, error=error)

        # Attempt interactive login
        login_success = trigger_oauth_login(interactive=True)

        if login_success:
            # Login succeeded, read new credentials
            try:
                creds = read_credentials()
                if creds and creds.is_valid:
                    self._current_credentials = creds
                    self._current_state = AuthState.OAUTH_VALID
                    return AuthenticationResult(
                        state=AuthState.OAUTH_VALID, credentials=creds
                    )
            except Exception:
                pass

        # Login failed
        if self.config.allow_fallback and self.config.api_key:
            # Fallback to API key
            warnings.warn(
                "OAuth login failed, falling back to API key mode.", stacklevel=2
            )
            self._current_state = AuthState.API_KEY_MODE
            return AuthenticationResult(
                state=AuthState.API_KEY_MODE, api_key=self.config.api_key
            )
        else:
            # No fallback allowed or no API key
            self._current_state = AuthState.AUTH_FAILED
            error = self.config.format_error_message(
                "OAuth login failed",
                suggestions=[
                    "Try running 'claude /login' manually",
                    "Set ANTHROPIC_API_KEY environment variable",
                    "Check your internet connection",
                ],
            )
            return AuthenticationResult(state=AuthState.AUTH_FAILED, error=error)

    def ensure_authenticated(self, force_refresh: bool = False) -> AuthenticationResult:
        """Ensure authentication is valid, refreshing/logging in if needed.

        This is the main entry point for authentication. Call this before
        each API request to ensure valid credentials.

        Args:
            force_refresh: Force re-detection of auth state

        Returns:
            AuthenticationResult with current auth state and credentials

        Raises:
            RuntimeError: If authentication fails and strict mode is enabled

        Example:
            >>> manager = AuthenticationManager()
            >>> result = manager.ensure_authenticated()
            >>> if result.is_ready:
            ...     headers = result.get_auth_header()
            ...     # Make API request with headers
        """
        # Detect current state (or use cached state)
        if force_refresh or self._current_state is None:
            self._current_state = self.detect_auth_state()

        current_state = self._current_state

        # Handle each state
        if current_state == AuthState.API_KEY_MODE:
            # Using API key
            return AuthenticationResult(
                state=AuthState.API_KEY_MODE, api_key=self.config.api_key
            )

        elif current_state == AuthState.OAUTH_VALID:
            # OAuth valid, return current credentials
            return AuthenticationResult(
                state=AuthState.OAUTH_VALID, credentials=self._current_credentials
            )

        elif current_state == AuthState.OAUTH_REFRESH_NEEDED:
            # Need to refresh token
            result = self.handle_oauth_refresh()
            # Check if strict mode and result is failed
            if result.state == AuthState.AUTH_FAILED and self.config.strict_mode:
                raise RuntimeError(result.error or "Authentication failed")
            return result

        elif current_state == AuthState.OAUTH_LOGIN_NEEDED:
            # Need to login
            result = self.handle_oauth_login()
            # Check if strict mode and result is failed
            if result.state == AuthState.AUTH_FAILED and self.config.strict_mode:
                raise RuntimeError(result.error or "Authentication failed")
            return result

        elif current_state == AuthState.AUTH_FAILED:
            # Authentication failed
            error = self.config.format_error_message(
                "No valid authentication method available",
                suggestions=[
                    "Run 'claude /login' to authenticate with OAuth",
                    "Set ANTHROPIC_API_KEY environment variable",
                    "Check your authentication configuration",
                ],
            )
            if self.config.strict_mode:
                raise RuntimeError(error)
            return AuthenticationResult(state=AuthState.AUTH_FAILED, error=error)

        else:
            # Unknown state (shouldn't happen)
            raise RuntimeError(f"Unknown authentication state: {current_state}")

    def get_current_state(self) -> AuthState | None:
        """Get current authentication state without triggering refresh/login.

        Returns:
            Current AuthState if known, None if not yet detected
        """
        return self._current_state

    def reset_state(self) -> None:
        """Reset authentication state, forcing re-detection on next call.

        Use this if credentials were updated externally (e.g., manual login).
        """
        self._current_state = None
        self._current_credentials = None


def get_authenticated_headers(
    auth_mode: str | None = None,
    auth_fallback: str | None = None,
    auth_interactive: bool | None = None,
) -> dict[str, str]:
    """Convenience function to get authentication headers.

    This is a simple wrapper around AuthenticationManager for
    one-off authentication needs.

    Args:
        auth_mode: Authentication mode (auto|oauth|api_key)
        auth_fallback: Fallback policy (enabled|disabled|strict)
        auth_interactive: Allow browser login prompts

    Returns:
        Dictionary with auth headers for API requests

    Raises:
        RuntimeError: If authentication fails

    Example:
        >>> headers = get_authenticated_headers()
        >>> # Use headers in API request
    """
    manager = AuthenticationManager(
        auth_mode=auth_mode,
        auth_fallback=auth_fallback,
        auth_interactive=auth_interactive,
    )
    result = manager.ensure_authenticated()

    if not result.is_ready:
        raise RuntimeError(result.error or "Authentication failed with unknown error")

    return result.get_auth_header()
